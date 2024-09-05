import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';
import ColumnResizer from 'column-resizer';

import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import TableContainer from '@material-ui/core/TableContainer';
import Table from '@material-ui/core/Table';
import TableHead from '@material-ui/core/TableHead';
import TableBody from '@material-ui/core/TableBody';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Skeleton from '@material-ui/lab/Skeleton';
import Box from '@material-ui/core/Box';

import UiState from 'data/ui_state';
import {PaginationComponent, OnlyPagerComponent} from 'common-ui/components/generic_components';
import f from 'common-ui/utils/f';
import VContextMenu from 'common-ui/components/v_context_menu';

@observer
export default class CommonTable extends Component {
    constructor(props) {
        super(props);
        this.table = React.createRef();
        this.state = this.getSortingState();
        this.tableId = props.tableId || "table";
        this.isColumnResizerLoading = null;
        this.initializeSession();
    }
    initializeSession = () => {
        if(this.props.resizable){
            try {
                this.store = sessionStorage;
            } catch (e) {
                this.store = {};
            }
        }
    }
    componentDidMount() {
        if (this.props.resizable) {
            if(!this.props.tableId){
                console.warn("Please provide table id to use column resizable feature");
            }
            this.enableResize();
        }
    }
    restoreColResizeState() {
        let data = UiState.getStateData("columnResizeTableData")
        if (data && data[this.tableId]) {
            this.store[this.tableId] = data[this.tableId];
        }
    }
    componentWillUnmount() {
        if (this.props.resizable && this.resizer) {
            let { store } = this.resizer;
            let columnResizeTableData = UiState.getStateData("columnResizeTableData") || {};
            columnResizeTableData[this.tableId] = store[this.tableId];
            let data = JSON.stringify(columnResizeTableData );
            UiState.saveState("columnResizeTableData", data);
            this.disableResize();
        }
    }
    componentDidUpdate() {
        if (this.props.resizable) {
            this.enableResize();
        }
    }

    enableResize() {
        const tableNode = this.table && this.table.current;
        let { resizableOptions, data } = this.props;
        let options = CommonTable.defaultProps.resizableOptions;
        Object.assign(options, resizableOptions)

        if (tableNode && this.isColumnResizerLoading != f.isLoading(data)) {
            this.restoreColResizeState();
            if (this.store && this.store[this.tableId]) {
                options.widths = this.store[this.tableId].split(';').map(w => Number(w));
            }
            this.resizer = new ColumnResizer(tableNode, options);
            this.resizer.tb.classList.remove('grip-padding');
            this.isColumnResizerLoading = f.isLoading(data);
        }
        // To sync resizable and origin table columns
        this.resizer?.syncGrips();
        this.resizer?.applyBounds();
    }

    disableResize() {
        if (this.resizer) {
            this.resizer.reset({ disable: true });
        }
    }

    getSortingState = () => {
        if (!this.props.tableAttr || !this.props.tableAttr.isSortingEnabled) {
            return {};
        }
        const { tableAttr: { columnToSort=[], sortDirection='', defaultSort={} } } = this.props;
        const { column='', direction=''} = defaultSort;
        return { columnToSort : column ? [column] :  columnToSort,  sortDirection: direction ? direction:  sortDirection }
    }

    descendingComparator = (a, b, orderBy) => {
        if (b[orderBy] < a[orderBy]) {
          return -1;
        }
        if (b[orderBy] > a[orderBy]) {
          return 1;
        }
        return 0;
    }
      
    getComparator = (order, orderBy) => {
        return order === 'desc'
          ? (a, b) => this.descendingComparator(a, b, orderBy)
          : (a, b) => -this.descendingComparator(a, b, orderBy);
    }
      
    stableSort = (array, comparator) => {
        const stabilizedThis = array.map((el, index) => [el, index]);
        stabilizedThis.sort((a, b) => {
          const order = comparator(a[0], b[0]);
          if (order !== 0) return order;
          return a[1] - b[1];
        });
        return stabilizedThis.map((el) => el[0]);
    }

    getHeaders() {
        const { tableAttr : { isSortingEnabled, onSort, columnToSort: expectedColSort }, getHeaders } = this.props;
        const { columnToSort, sortDirection } = this.state;

        return (
            <TableHead data-testid="thead">
                <TableRow>
                    {
                        isSortingEnabled
                        ?
                            getHeaders && getHeaders(this.options).map((headCell, idx) => {
                                const { props: { column='', children, ...rest }, key } = headCell;
                                return (
                                    <TableCell
                                        key={key}
                                        sortDirection={sortDirection}
                                        align='left'
                                        {...rest}
                                    >
                                        <TableSortLabel
                                            active={columnToSort.includes(column)}
                                            className={`${!expectedColSort.includes(column) && 'hide-sorticon'}` }
                                            hideSortIcon={!expectedColSort.includes(column)}
                                            direction={columnToSort.includes(column) ? sortDirection: 'asc'}
                                            onClick={(e) => {
                                                if(!expectedColSort.includes(column)) return;
                                                const isAsc = columnToSort.includes(column) && sortDirection === 'asc';
                                                this.setState({ sortDirection: isAsc ? 'desc' : 'asc', columnToSort: [column] }, () => {
                                                    onSort && onSort({direction: this.state.sortDirection.toUpperCase(), column: column});
                                                });
                                            }}
                                        >
                                            {children}
                                        </TableSortLabel>
                                    </TableCell>
                                )
                            })
                        :
                            getHeaders && getHeaders(this.options)
                    }
                </TableRow>
                {this.getFilters()}
            </TableHead>
        )
    }
    getFilters() {
        const { filters } = this.props
        if (filters) {
            return (
                <TableRow className="table-search-row">
                    {filters().map((filter, index) => {
                        let props = {}
                        if (filter.colSpan) {
                            props.colSpan = filter.colSpan;
                        }
                        return (
                            <TableCell key={filter.column || index} {...props}>
                                {filter.component}
                            </TableCell>
                        )
                    })}
                </TableRow>
            )
        }
        return null
    }
    getRows() {
        let {getRowData, getHeaders, isRowCustom,onRowClick, renderCustomBody, loading, tableAttr: {isSortingEnabled}} = this.props;
        let {options: { models, modelsLength }, stableSort, getComparator, state} = this; 
        const { sortDirection, columnToSort} = state;
        const customizedRow = isSortingEnabled ? stableSort(models, getComparator(sortDirection, columnToSort)) : models;
        if(!modelsLength || loading) {
            const headerColumnCount = getHeaders ? getHeaders(this.options).length : 0;
            return (
                <TableBody data-testid="tbody-with-nodata">
                    <TableRow data-testid="table-row">
                        <TableCell colSpan={headerColumnCount} className="alignment-emptystate">
                            {this.getNoDataText()}
                        </TableCell>
                    </TableRow>
                </TableBody>
            )
        }

        if (renderCustomBody) {
            // use data-testid property while invoking renderCustomBody
            return renderCustomBody("tbody-with-data");
        }

        return (
            <TableBody data-testid="tbody-with-data">
                {customizedRow.map((model, i) => {
                    if (isRowCustom) {
                        return getRowData && getRowData(model, i, this.options)
                    }
                    return (
                        <TableRow
                            key={model.id || i}
                            hover
                            data-testid="table-row"
                            onClick={(e) => {
                                onRowClick && onRowClick(e, model, i)
                            }}
                        >
                            {getRowData && getRowData(model, i, this.options)}
                        </TableRow>
                    )
                })}
            </TableBody>
        )
    }

    setPageNumberInParam(page) {
        const {data} = this.props;
        if (data && data.params) {
            data.params.page = page-1  || undefined;
        }
    }
    handlePageChange = (...args) => {
        const {pageChange} = this.props;
        this.setPageNumberInParam(...args);
        pageChange && pageChange(...args);
    }

    setRowSizeInParam(size) {
        const {data} = this.props;
        if (data && data.params) {
            data.params.size = size || data.params.size;
        }
    }

    handleSizeChange = (...args) => {
        const {onChange} = this.props.rowsPerPageAttr;
        this.setRowSizeInParam(Number(args[0]));
        this.setPageNumberInParam(1);
        onChange && onChange(Number(args[0]));
    }

    getPagination() {
        const {data, boxAttr, pageAttr, rowsPerPageAttr, pagination, pagerComponent, _vState, showTotalRecordCount, paginationGridAttr} = this.props;

        if (pagination && data) {
            return (
                <Box display="flex" data-testid="table-pagination" {...boxAttr}  >
                    {
                        pagerComponent ? 
                        <OnlyPagerComponent
                            promiseData={data}
                            callback={this.handlePageChange}
                            {...pageAttr}
                            _vState={_vState}
                        /> :
                        <PaginationComponent
                            promiseData = {data}
                            callback={this.handlePageChange}
                            {...pageAttr}
                            {...rowsPerPageAttr}
                            paginationGridAttr={paginationGridAttr}
                            onChange={this.handleSizeChange}
                            showTotalRecordCount={showTotalRecordCount}
                        />
                    }
                </Box>
            )
        }
        return null
    }
    getContextMenu() {
        const {showContextMenu, onContextMenuSelection} = this.props;
        if (showContextMenu) {
            return <VContextMenu tabelrefs={this.table.current} callback={onContextMenuSelection} />
        }
        return null;
    }
    getNoDataText = () => {
        const {data, loading, noDataText} = this.props;

        if (loading) {
            return this.getSkeletonWrapper();
        }
        if (f.isPromise(data)) {
            return f.isLoading(data) ? this.getSkeletonWrapper() : (<Box  data-testid="table-noData">{noDataText}</Box>);
        }
        return noDataText;
    }

    getSkeletonWrapper = () => {
        return (
            <Box p={1} data-testid="loader">
                <Skeleton variant="text" animation="wave" width="100%" />
                <Skeleton variant="text" animation="wave" width="100%" />
                <Skeleton variant="text" animation="wave" width="100%" />
                <Skeleton variant="text" animation="wave" width="100%" />
            </Box>
        )
    }
    render() {
        const {tableRowAttr, tableResponsive, tableColAttr, tableAttr, getHeaders, paperProps, addTableRowCol, data,
            tableClassName, hasElevation, paperChild
        } = this.props;
        const {defaultSort, onSort, columnToSort, sortDirection, isSortingEnabled, ...restTableAttr} = tableAttr;

        let models = f.isPromise(data) ? f.models(data) : data;
        this.options = {
            models: models,
            modelsLength: models.length,
            promiseObj: data
        }
        let idTableAttr = {};
        if(this.props.resizable){
            idTableAttr = { id : this.tableId };
        }

        let table = (
            <Fragment>
                <TableContainer >
                    <Table className={`table-header-bg ${tableClassName ? tableClassName : ''}`}
                        data-test="table"
                        ref={this.table}
                        {...idTableAttr}
                        {...restTableAttr}
                    >
                        {this.getHeaders()}
                        {this.getRows()}
                    </Table>
                </TableContainer>
                {this.getPagination()}
            </Fragment>
        )

        if (hasElevation) {
            table = (
                <Paper {...paperProps}>
                    {paperChild}
                    {table}
                </Paper>
            )
        }

        if(addTableRowCol) {
            table = (
                <Grid container spacing={3} {...tableRowAttr}>
                    <Grid item xs={12} {...tableColAttr}>
                        {table}
                    </Grid>
                </Grid>
            )
        }
        return (
            <Fragment>
                {table}
                <br/>
                {this.getContextMenu()}
            </Fragment>
        )
    }
}

CommonTable.defaultProps = {
    data: f.initCollection(),
    noDataText: "No matching records found.",
    tableRowAttr: {},
    tableColAttr: {},
    tableAttr: {
        defaultSort: {}
    },
    tableResponsive: {},
    pageRowAttr: {},
    pageColAttr: {},
    pageAttr: {},
    rowsPerPageAttr: {},
    paginationGridAttr: {},
    getHeaders: null,
    getRowData:  null,
    filters: null,
    pagination: true,
    pageChange: null,
    isRowCustom: false,
    showContextMenu: false,
    addTableRowCol: true,
    loading: false,
    onContextMenuSelection: () => {},
    renderCustomBody: null,
    tableSort: () => ( {} ),
    paperChild: null,
    paperProps: {},
    hasElevation: true,
    resizable: false,
    showTotalRecordCount: false,
    resizableOptions: {
        liveDrag: true,
        // minWidth: 30,
        headerOnly: true,
        resizeMode: "overflow",
        draggingClass:"rangeDrag",
        gripInnerHtml:'<div class="rangeGrip">\
        <svg className="MuiSvgIcon-root jss165 MuiSvgIcon-fontSizeSmall" focusable="false" viewBox="0 0 24 24"\
             aria-hidden="true" title="fontSize small">\
            <path\
                d="M11 18c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zm-2-8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm6 4c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"></path>\
        </svg></div>'
    }
}