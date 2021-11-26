import pandas as pd
import param
import numpy as np

from pyhdx import TorchFitResult
from pyhdx.fitting import RatesFitResult
from pyhdx.models import HDXMeasurement, HDXMeasurementSet
from pyhdx.support import multiindex_astype, multiindex_set_categories


class AppSourceBase(param.Parameterized):
    """Base class for sources"""

    _type = 'base'

    updated = param.Event()

    def get(self):
        raise NotImplementedError()


class TableSource(AppSourceBase):

    tables = param.Dict({})

    _type = 'table'

    def get(self):
        if len(self.tables) == 1:
            return next(iter(self.tables.values))
        else:
            raise ValueError("TableSource has multiple tables, use `get_table`")

    def get_table(self, table):
        df = self.tables.get(table, None)

        return df

    def get_tables(self):
        """
        Returns the list of tables available on this source.
        Returns
        -------
        list
            The list of available tables on this source.
        """

        return list(self.tables.keys())


class PyHDXSource(TableSource):
    _type = 'pyhdx'

    # table options are (table_name, (opts)):  (General: <quantity>_<specifier> -> opts[qty] for colors
    # peptides
    # index: peptide_id
    # columns: state, exposure, quantity

    # rfu_residues (rfu)
    # index: r_number
    # columns: state, exposure (TODO add quantity)

    # rates
    # index: r_number
    # columns: guess_ID, state, quantity

    # dG_fits (dG)
    # index: r_number
    # columns: fit_ID, state, quantity

    # ddG_comparison (ddG)
    # index: r_number
    # columns: comparison_name, comparison_state, quantity

    # d_calc
    # index: exposure
    # columns: fit_ID, state, peptide_id, quantity

    # loss
    # index: epoch
    # columns: fit_ID, loss_type

    # peptide_mse
    # index: peptide_id
    # columns: fit_ID, state, quantity

    # d_calc
    # peptide_mse (has colormap but not user configurable)

    hdxm_objects = param.Dict({})
    rate_results = param.Dict({})  # dataframes?
    dG_fits = param.Dict({})

    def from_file(self):
        pass
        # todo load hdxms first
        #then use those to reload dG results

    def add(self, obj, name):  # todo Name is None and use obj name?
        if isinstance(obj, HDXMeasurement):
            self._add_hdxm_object(obj, name)
        elif isinstance(obj, TorchFitResult):
            self._add_dG_fit(obj, name)
        elif isinstance(obj, RatesFitResult):
            self.rate_results[name] = obj
            self.param.trigger('rate_results')
        else:
            raise ValueError(f"Unsupported object {obj!r}")

    @property
    def hdx_set(self):
        return HDXMeasurementSet(list(self.hdxm_objects.values()))

    def _add_hdxm_object(self, hdxm, name):  # where name is new 'protein state' entry (or used for state (#todo clarify))
        # Add peptide data
        df = hdxm.data_wide.copy()
        tuples = [(name, *tup) for tup in df.columns]
        columns = pd.MultiIndex.from_tuples(tuples, names=['state', 'exposure', 'quantity'])
        df.columns = columns
        self._add_table(df, 'peptides')

        # Add rfu per residue data
        df = hdxm.rfu_residues
        tuples = [(name, column) for column in df.columns]  # todo the rfus need an additional level (rfu / name:quantity)
        columns = pd.MultiIndex.from_tuples(tuples, names=['state', 'exposure'])
        df.columns = columns
        self._add_table(df, 'rfu_residues')

        self.hdxm_objects[name] = hdxm
        self.param.trigger('hdxm_objects')
        self.updated = True

    def _add_dG_fit(self, fit_result, name):
        # Add deltaG values table (+ covariances etc)
        df = fit_result.output.copy()
        tuples = [(name, *tup) for tup in df.columns]
        columns = pd.MultiIndex.from_tuples(tuples, names=['fit_ID', 'state', 'quantity'])
        df.columns = columns
        self._add_table(df, 'dG_fits')

        # Add calculated d-uptake values (#todo add method on FitResults object that does this?)
        timepoints = fit_result.hdxm_set.timepoints
        tmin = np.log10(timepoints[np.nonzero(timepoints)].min())
        tmax = np.log10(timepoints.max())
        pad = 0.05 * (tmax - tmin)  # 5% padding percentage

        tvec = np.logspace(tmin - pad, tmax + pad, num=100, endpoint=True)
        d_calc = fit_result(tvec)

        # Reshape the d_calc numpy array (Ns x Np x Nt to pandas dataframe (index: Ns, columns: multiiindex Ns, Np)
        Ns, Np, Nt = d_calc.shape
        reshaped = d_calc.reshape(Ns * Np, Nt)
        columns = pd.MultiIndex.from_product(
            [[name], fit_result.hdxm_set.names, np.arange(Np), ['d_calc']],
            names=['fit_ID', 'state', 'peptide_id', 'quantity'])
        index = pd.Index(tvec, name='exposure')
        df = pd.DataFrame(reshaped.T, index=index, columns=columns)
        df = df.loc[:, (df != 0).any(axis=0)]  # remove zero columns, replace with NaN when possible
        self._add_table(df, 'd_calc')

        # Add losses df
        df = fit_result.losses.copy()
        tuples = [(name, column) for column in df.columns]  # losses df is not multiindex
        columns = pd.MultiIndex.from_tuples(tuples, names=['fit_ID', 'loss_type'])
        df.columns = columns
        self._add_table(df, 'loss')

        #Add MSE per peptide df
        squared_errors = fit_result.get_squared_errors()
        dfs = {}
        for mse_sample, hdxm in zip(squared_errors, fit_result.hdxm_set):
            peptide_data = hdxm[0].data
            mse = np.mean(mse_sample, axis=1)
            # Indexing of mse_sum with Np to account for zero-padding
            passthrough_fields = ['start', 'end', 'sequence']
            df = peptide_data[passthrough_fields].copy()
            df['peptide_mse'] = mse[:hdxm.Np]
            dfs[hdxm.name] = df

        # current bug: convert dtypes drop column names: https://github.com/pandas-dev/pandas/issues/41435
        # use before assigning column names
        mse_df = pd.concat(dfs.values(), keys=dfs.keys(), axis=1).convert_dtypes()
        mse_df.index.name = 'peptide_id'
        tuples = [(name, *tup) for tup in mse_df.columns]
        columns = pd.MultiIndex.from_tuples(tuples, names=['fit_ID', 'state', 'quantity'])
        mse_df.columns = columns
        self._add_table(mse_df, 'peptide_mse')

        self.dG_fits[name] = fit_result
        self.updated = True

    def _fit_results_updated(self):  #todo method name / result dicts names
        combined = pd.concat([fit_result.output for fit_result in self.dG_fits.values()], axis=1,
                             keys=self.dG_fits.keys(), names=['fit_ID', 'state', 'quantity'])
        self.tables['dG_fits'] = combined

        self.updated = True

        # todo add d_exp etc
        #cached?:

    @param.depends('rate_results', watch=True)
    def _rates_results_updated(self):
        combined = pd.concat([fit_result.output for fit_result in self.rate_results.values()], axis=1,
                             keys=self.rate_results.keys(), names=['guess_ID', 'state', 'quantity'])
        self.tables['rates'] = combined

        self.updated = True

    def _add_table(self, df, table, categorical=True):
        """

        :param df:
        :param table:
        :param categorical: True if top level of multiindex should be categorical
        :return:
        """
        if table in self.tables:
            current = self.tables[table]
            new = pd.concat([current, df], axis=1)
            categories = list(current.columns.unique(level=0)) + list(df.columns.unique(level=0))
        else:
            new = df
            categories = list(df.columns.unique(level=0))
        if categorical:
            new.columns = multiindex_astype(new.columns, 0, 'category')
            new.columns = multiindex_set_categories(new.columns, 0, categories, ordered=True)
        self.tables[table] = new


