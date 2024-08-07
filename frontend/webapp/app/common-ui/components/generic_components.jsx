import React, {Component, createRef, Fragment, useState} from 'react';

import {reaction, observable, action} from 'mobx';
import {observer, Observer} from 'mobx-react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import {uniq, isArray, isUndefined} from 'lodash';
import isDebounce from 'lodash/debounce';
import InfiniteScroll from 'react-infinite-scroll-component';

// Material Imports
import ViewColumnIcon from '@material-ui/icons/ViewColumn';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import { Container } from '@material-ui/core';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';
import MoreVertIcon from '@material-ui/icons/MoreVert';
import ClickAwayListener from '@material-ui/core/ClickAwayListener';
import Grow from '@material-ui/core/Grow';
import Popper from '@material-ui/core/Popper';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Grid from '@material-ui/core/Grid';
import Tooltip from '@material-ui/core/Tooltip';
import FileCopyIcon from '@material-ui/icons/FileCopy';
import Paper from '@material-ui/core/Paper'
import TextField from '@material-ui/core/TextField';
import Divider from '@material-ui/core/Divider';
import Box from '@material-ui/core/Box';
import Pagination from '@material-ui/lab/Pagination';
import Chip from '@material-ui/core/Chip';
import Popover from '@material-ui/core/Popover';
import { makeStyles } from '@material-ui/core/styles';
import LinearProgress from '@material-ui/core/LinearProgress';
import Typography from '@material-ui/core/Typography';
import ArrowForwardIcon from '@material-ui/icons/ArrowForward';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import ClearIcon from '@material-ui/icons/Clear';
import Skeleton from '@material-ui/lab/Skeleton';
import Collapse from '@material-ui/core/Collapse';
import KeyboardArrowDownIcon from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@material-ui/icons/KeyboardArrowUp';
import CircularProgress from '@material-ui/core/CircularProgress';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import ArrowRightAltSharpIcon from '@material-ui/icons/ArrowRightAltSharp';
import {withStyles} from '@material-ui/core/styles';
import LoopIcon from '@material-ui/icons/Loop';
import CancelIcon from '@material-ui/icons/Cancel';

import allStores from 'data/stores/all_stores';
import f from 'common-ui/utils/f';
import MLookupResource from 'common-ui/data/models/m_resource_lookup';
import {ttl, makeAccessDeniedTagProgressData} from 'common-ui/components/view_helpers';
import {Utils} from 'common-ui/utils/utils';
import FsSelect from 'common-ui/lib/fs_select/fs_select';
import KeyEvent from 'common-ui/lib/react-structured-filter/keyevent';
import tourManagerUtil from 'common-ui/utils/tour_manager_util';
import {ValidationMsgField, FormGroupSelect2} from 'common-ui/components/form_fields';
import { Checkbox } from 'common-ui/components/filters';
import {Ibox} from 'common-ui/components/widgets';
import {ROWS_PER_PAGE, RESOURCE_SERVICE} from 'common-ui/utils/globals';

@observer
class Select2 extends Component {
  render () {
    const {labelKey, valueKey} = this.props;
    return (
      <FsSelect {...this.props}
        labelKey={labelKey}
        valueKey={valueKey}
      />
    )
  }
}

Select2.defaultProps = {
  labelKey: 'label',
  valueKey: 'value'
}

const Loader = observer(function Loader({
    isLoading=false, 
    promiseData, 
    fields, 
    attrName, 
    height="300px", 
    size="large", 
    loaderContent, 
    noDataGridProps = {},
    noDataBoxProps = {},
    noDataWrapRow = false,
    dataTestId = "loader",
    ...props}) {

  let loader = (
    <Grid item xs={props.colSize} className='chart-loader' data-testid={dataTestId}>
      {loaderContent ? loaderContent : <div style={{height: height}}>{ttl(size)}</div>}
    </Grid>
  );

  let loading = false;
  if ((f.isPromise(promiseData) && f.isLoading(promiseData)) || isLoading) {
    loading = true;
  } else if (fields && attrName) {
    if (typeof fields[attrName] == 'object') {
      loading = !fields[attrName];
    } else {
      loading = !!fields[attrName];
    }
  }
  if (loading) {
    return loader;
  }
  if ((props.handleNoData && f.isPromise(promiseData) && !f.isLoading(promiseData) && !f.models(promiseData).length) || (props.handleNoData && props.showNoData) ) {
    const  noDataComponent = (
      <Box data-testid="noData" display="flex" justifyContent="center" alignItems="center" height="300px" {...noDataBoxProps}>
        <Typography variant='subtitle1' color="textSecondary" >{props.noDataTitle || "No data to display"}</Typography>
      </Box>
    )

    if (noDataWrapRow) {
      return (
        <Grid item xs={12} {...noDataGridProps}>
          {noDataComponent}
        </Grid>
      )
    }
    return noDataComponent;
  }
  if (typeof props.children == 'function') {
    return <div>{props.children()}</div>;
  }
  return <Fragment>{props.children}</Fragment>;

})

const RowsPerPageComponent = ({ onChange, size }) => {
  return(
    <Box display="flex" alignItems="center" px="5px" data-testid="rows_per_page">
      <Box component='span' p={1}>Rows per page</Box>
      <Select2
        value={size}
        data={ROWS_PER_PAGE}
        labelKey={'rows'}
        valueKey={'rows'}
        onChange={onChange}
        disableClearable={true}
      />
    </Box>  
  );
}

const PaginationComponent = observer(function PaginationComponent({
  promiseData, callback, showRowsPerPage, onChange, showPageOf=true, minimumPage = 1,
  showTotalRecordCount = false, paginationGridAttr
}) {

  if (!promiseData) {
    return null;
  }
  let pageState = f.isPromise(promiseData) ? f.pageState(promiseData) : {};
  if (f.isFulfilled(promiseData) && !f.isLoading(promiseData) && pageState) {
    let {number, numberOfElements, size, totalElements, totalPages} = pageState;

    const showPaginationComp = pageState.totalPages > minimumPage; 

    let pageButtons = [];

    let maxButtons = 5;
    let items = totalPages;

    let activePage = number + 1;

    let startPage;
    let endPage;

    if (items > maxButtons) {
      startPage = Math.max(Math.min(activePage - Math.floor(maxButtons / 2, 10), items - maxButtons + 1), 1);
      endPage = startPage + maxButtons - 1;
    } else {
      startPage = 1;
      endPage = items;
    }

    const onSelect = (page) => {
      if (activePage != page && callback) {
        callback(page);
      }
    }

    const handleChangePage = (event, newPage) => {  
      onSelect(newPage);
    };

    if (!showRowsPerPage && !showPaginationComp) {
      return null;
    }

    return (
      <Grid container justify="flex-end" >
        <Grid item xs={12} md={4}>
          {showTotalRecordCount && (<Box display="flex" justifyContent="flex-start" pt={2} pb={1} pl={2} pr={2}>
            <div>{"Total Records: " + totalElements}</div>
          </Box>)
          }
        </Grid>
        <Grid item xs={12} md={8} {...paginationGridAttr}>
          <Box display="flex" justifyContent="flex-end" alignItems="center" pt={1} pb={1} pl={2} pr={2}>
            {
              pageState.numberOfElements > 0 && showRowsPerPage && <RowsPerPageComponent onChange={onChange} size={size}/>
            }
            {showPaginationComp && 
              <Fragment>
                {
                  showPageOf && <CustomPageInput data-testid="custom-page-input" totalPages={totalPages} activePage={activePage} handlePage={handleChangePage}/>
                }
                <Pagination 
                  data-testid="pagination"
                  data-track-id="pagination"
                  page={activePage}
                  count ={totalPages}
                  showFirstButton
                  showLastButton
                  onChange={handleChangePage}
                />
              </Fragment>
            }
          </Box>
        </Grid>
      </Grid>
    )
  }
  return null;
});

const CustomPageInput = ({ totalPages, activePage, handlePage }) => {
  const [pageValue, setPageValue] = useState(activePage)
  return (
      <Box display="flex" justifyContent="space-evenly" bgcolor="background.paper">
        <Box component='span' p={1}>Page</Box>
          <Divider orientation="vertical" flexItem />
        <Box width="35px">
          <TextField 
            value={pageValue}
            inputProps={{style: { textAlign: 'center' }}}
            data-track-id="page-jump"
            onChange = {(e) => {
              setPageValue(Number(e.target.value) || '');
            }}
            onKeyDown={(e) => {
              if(e.keyCode == 13){
                const targetVal = Number(e.target.value);
                if(!isNaN(targetVal)) {
                  let valEntered = targetVal;
                  if (targetVal < 1){
                    valEntered = 1
                  } else if (targetVal > totalPages) {
                    valEntered = totalPages;
                  }
                  setPageValue(valEntered);
                  handlePage(null, valEntered);
                }
              }
            }}
          />
        </Box>
          <Divider orientation="vertical" flexItem />
        <Box component='span' p={1}>of {totalPages}</Box>
      </Box>
  )
}

@observer
class CustomPagination extends Component {
  regEx= /^\d+$/
  @observable _vPageState = {
    page: 1
  }


  constructor(props) {
    super(props);
    this.setPage();
    this.dipose = reaction(
      () => !f.isLoading(props.promiseData),
      () => {
        if ( !f.isLoading(props.promiseData)) {
          this.setPage();
        }
      }
    )
  }

  setPage = () => {
    let pageState = f.pageState(this.props.promiseData);
    if (pageState && (pageState.number+1) != this._vPageState.page) {
      this._vPageState.page = pageState.number + 1;
    }
  }

  componentWillUnmount = () => {
      // dispose the reaction method
      if (this.dispose) {
        this.dispose();
      }
      delete this.dispose;
  }
  
  handleOnChange = (e) => {
    const {promiseData} = this.props;
    let page = e.target.value;
    if (parseInt(page) > f.pageState(promiseData).totalPages) {
      page = f.pageState(promiseData).totalPages;
    }
    let isValid = this.regEx.test(page);
    if (!page || isValid) {
      this._vPageState.page = page;
    }
  }
  handleOnKeyUp = (e) => {
    switch((e.keyCode || e.which)) {
      case KeyEvent.DOM_VK_RETURN:
      case KeyEvent.DOM_VK_ENTER:
        let page = this._vPageState.page;
        if (!page) {
          this._vPageState.page = 1;
        }
        this.props.callback && this.props.callback(this._vPageState.page);
        break;
    }
  }
  render() {
    const {promiseData} = this.props;
    return (
      <ul data-test="pagination-custom" className="pagination custom-pagination m-r-sm">
        <li><span>Page</span></li>
        <li>
          <input className="form-control" value={this._vPageState.page} onChange={this.handleOnChange} onKeyUp={this.handleOnKeyUp} />
        </li>
        <li><span>of {f.pageState(promiseData).totalPages}</span></li>
      </ul>
    )
  }
}

@observer
class OnlyPagerComponent extends Component {
  @observable _vPageState = {
    page: 1,
    prevNextValueList: ['']
  }
  pageChange = ({ previous }) => {
    this.props.callback && this.props.callback(previous);
  }
  render() {
    const { promiseData, _vState } = this.props;
    if (f.isFulfilled(promiseData) && f.isLoading(promiseData)) {
      return null;
    }
    let pageState = f.pageState(promiseData);

    return (
      <Fragment>
        {
          <Grid container spacing={3} justify="center" className="m-t-xs m-b-xs">
            <Grid item sm={8} className="text-center">
              {
                _vState.prevNextValueList && _vState.prevNextValueList.length > 1 &&
                <Button variant="outlined" color="primary" size="small" onClick={() => {
                  this.pageChange({ previous: true })
                }}>
                  <ArrowRightAltSharpIcon className="m-r-xs rotate-180" fontSize="small"/> Previous Page 
                </Button>
              }
              {
                (_vState.showNextPage != null ? _vState.showNextPage : (pageState.last == false)) &&
                <Button variant="outlined" color="primary" size="small" className="m-l-sm" onClick={() => {
                  this.pageChange({ previous: false })
                }} >Next Page 
                  <ArrowRightAltSharpIcon className="m-l-xs" fontSize="small"/>
                </Button>
              }
            </Grid>
          </Grid>
        }
      </Fragment>
    )
  }
}



const getTooltipOverlay = ({
  tooltipContent,
  open, 
  anchorEl,
  handleClose,  
  placement = {
    vertical: 'top',
    horizontal: 'center',
  }, 
  anchorPlacement = {
    vertical: 'bottom',
    horizontal: 'center',
  },
  trigger,
  className
}) => {

  return (
    <CustomPopover open={open} 
      getTarget={anchorEl} 
      close={handleClose} 
      popoverContent={tooltipContent} 
      anchorOrigin={anchorPlacement} 
      transformOrigin={placement}
      trigger={trigger}
      className={`popover-general ${className}`}
    />
  )
}

const TooltipOverlay = observer(({placement, onOpen, anchorElProp, trigger=['hover', 'click'], overlay=null, className, tooltipContent, children, anchorPlacement}) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const getTriggers = () => {
    const actions = {};
    trigger.forEach((el) => {
      switch (el) {
        case 'hover':
          actions.onMouseEnter = handleOpen;
          actions.onMouseLeave = handleClose;
          break;
        case 'focus':
          actions.onFocus = handleOpen;
          break;
        default: actions.onClick = handleOpen;
      }
    });
    return actions;
  }
  const handleOpen = (event) => {
    event.stopPropagation();
    setAnchorEl(anchorElProp || event.currentTarget);
    if (onOpen) {
      onOpen(handleClose)
    }
  };

  const handleClose = (e) => {
    e.stopPropagation();
    setAnchorEl(null);
  };

  if (tooltipContent) {
    overlay = getTooltipOverlay({tooltipContent, open: Boolean(anchorEl), anchorEl, handleClose, placement, anchorPlacement, trigger, className})
  }
  if(!overlay) {
    return;
  }
  return (
    <ClickAwayListener onClickAway={handleClose}>
      <Fragment>
        <Box component="span" {...getTriggers()}>
          {children}
        </Box>
        {overlay}
      </Fragment>
    </ClickAwayListener>
  )
});

const TooltipOverlayInfo = observer(function TooltipOverlayInfo({tooltipContent}){
  return(
    <TooltipOverlay trigger={['hover', 'focus']} anchorPlacement={{vertical: 'top', horizontal: "center"}} placement={{vertical: 'bottom', horizontal: "center"}} 
      tooltipContent={tooltipContent}>
      <IconButton size="small">
          <InfoOutlinedIcon color="action" fontSize="inherit"/>
      </IconButton>
    </TooltipOverlay>
  )
});

const SingleTag = observer(function SingleTag({tag}) {
  return (
    <TooltipOverlay tooltipContent={tag}>
      <Chip size="small" color={'primary'} className="m-r-xs" label={tag} />
    </TooltipOverlay>
  )
});

const RemainingTags = observer(function RemainingTags({tags, sliceFrom}) {
  let remTags = tags.split(',').slice(sliceFrom).join(', ');
  return (
    <TooltipOverlay tooltipContent={remTags}>
      <Chip size="small" color={'primary'} className="m-r-xs tag-ellipsis" label="..." />
    </TooltipOverlay>
  )
});

const WrapTags = function WrapTags({variant="primary", children}) {
  return (
    <Chip size="small" color={variant} className="m-r-xs wrap-tags" label={children} />
  )
}

const VTagsSection = observer(({items=[], title, color='chip-info', margin='m-b-lg'}) => {
  if (items.length) {
    return (
      <div className={`${margin} text-left`}>
        { title && <div className="tags-section"><Typography variant="body2">{title}</Typography></div>}
        <div>
          {items.map((item,i)=>{
            return <Chip key={`item__${i}`} size="small" className={`m-r-xs ${color}`} label={item} />;
          })}
        </div>
      </div>
    )
  }
  return null;
});


const MessageHighLighter = observer(({_vState, messageList, fieldName, type}) => {
  const notExist =  messageList['status'] ? true : false;
  const msg = `The following rules will be affected as the ${type} "${_vState[fieldName]}" has been `;
  return (
    <div className={`tag-danger-section text-left`}>
      <CancelIcon fontSize="large" color="secondary"/>
      <Typography variant="subtitle2" color="secondary">
        {msg}<b>{`${notExist ? 'deleted' : 'disabled'}`}</b>.
      </Typography>
    </div>
  );
})

class VVerificationMessages extends Component {
  state={
    copyState: false
  }
  tooltipPos = {}
  handleMouseOut = ()=>{
    const node = document.querySelector('#tooltip-top');
    if (node !== null) {
      this.setState ({copyState : false}, () => {
        node.style.left = this.tooltipPos.left + 'px';
      });
    }
  }
  handleClick = ()=>{
    Utils.copyToClipboard('tags-sections-block');
    const node = document.querySelector('#tooltip-top');
    this.tooltipPos = node.getBoundingClientRect();
    this.setState ({copyState : true}, () => {
      const left = this.tooltipPos.left + ((this.tooltipPos.width - node.getBoundingClientRect().width) / 2);
      node.style.left = left + 'px';
    });
  }
  render(){
    const {messageList} = this.props._vState;
    const messageObj = messageList[0] || {};
    let hasDependency = 0;
    if (messageObj) {
      const { STRUCTURED = [], UNSTRUCTURED = [], POST_PROCESS = []} = messageObj;
      hasDependency = STRUCTURED.length  || UNSTRUCTURED.length || POST_PROCESS.length;
    }

  return (
    <Grid container spacing={3} className="tag-success-section">
      <Grid item xs={12}>
        {
          !hasDependency
          ?
            <Fragment>
              <Box mb={2}>
                <CheckCircleIcon className="text-success" fontSize="large" />
              </Box>
              <Typography variant="subtitle2" className="text-success">
                {`${this.props.type} "${this.props._vState.verifiedFeatureName}" verified successfully!`}
              </Typography>
              {/* <div>No disabled or deleted items found.</div> */}
            </Fragment>
          :
            <div className="clearfix tag-listing-block">
              <div className="tag-sections-container">
                <Fragment>
                  <MessageHighLighter _vState={this.props._vState} messageList={messageObj} fieldName={this.props.fieldName} type={this.props.type}/>
                  <div onMouseOut={this.handleMouseOut}>
                    <Tooltip placement="top" title={this.state.copyState  ? "Copied!" : "Copy to Clipboard"} id={`tooltip-top`} className="copy-tooltip">
                      <a className="pull-right" onClick={this.handleClick}>
                        <FileCopyIcon fontSize="small" />
                      </a>
                    </Tooltip>
                  </div>
                  <div id="tags-sections-block">
                    {messageList.map((msg, i)=>{
                      return ([
                        <VTagsSection key={i+1} items={msg["STRUCTURED"]} title="Structured" />,
                        <VTagsSection key={i+2} items={msg["UNSTRUCTURED"]} title="UnStructured" />,
                        <VTagsSection key={i+3} items={msg["POST_PROCESS"]} title="Post Processing" />
                      ]);
                    })}
                  </div>
                </Fragment>
              </div>
            </div>
          }
        </Grid>
      </Grid>
    );
  }
}

class FeedActivityList extends Component {
  getProgressBar(data) {
    let progressBar = (
      <Fragment>
        {
          //TODO need work around for displaying multiple style progress
          data.dataCount && data.dataCount.slice(0, 1).map((dc, i) => {
            return <LinearProgress color={dc.progressStyle === 'danger' ? 'secondary' : 'primary'} variant="determinate" value={dc.per || 0} key={i} />
          })
        }
      </Fragment>
    );
    if (data.dataCount && !data.dataCount.length) {
      progressBar = <LinearProgress variant={"determinate"} value={0} />
    }
    if (this.props.showPopover) {
      return (
        <TooltipOverlay tooltipContent={(
            <div className="percent-alert-popover dashboard-ranges">
              {data.dataCount && data.dataCount.map((dc, i) => {
                return ([
                  <span key={i}>
                    <span className={`badge m-r-xs ${dc.alertClassName} text-white border-round`}> </span>
                    <span className="popover-text">{dc.name.toUpperCase()} - <span className="pull-right">{dc.value}</span></span>
                  </span>, <br key={`${i}_br`} />
                ])
              })}
            </div>
          )}
        >
          {progressBar}
        </TooltipOverlay>
      )
    }
    return progressBar
  }
  render() {
    const {data, onClick} = this.props;

    return (
      <div className="feed-activity-list nomargin-feed">
        {
          data.map((obj) => {
            return (
              <div className="feed-element" key={obj.name} onClick={(e) => onClick && onClick(e, obj)} style={{cursor: onClick && 'pointer'}}>
                <h4 className="no-margins" title={obj.name}>{obj.name}&nbsp;</h4>
                <div className="stat-percent">{obj.total}</div>
                {this.getProgressBar(obj)}
              </div>
            )
          })
        }
      </div>
    )
  }
}
FeedActivityList.defaultProps = {
    showPopover: true
}

class MoreLessComponent extends Component{
  state = {
    isOpen: false
  }
  // items = [];
  
  constructor(props) {
    super(props);
    // this.items = this.props.list ? this.props.list : [];
  }

  toggle = () => {
    this.setState({ isOpen: !this.state.isOpen });
  }

  getRenderedItems() {
    if (this.state.isOpen) {
      return this.props.list ;
    }
    return (this.props.list || []).slice(0, this.props.Max_SizeToShow);
  }

  getRenderedString(renderedStringType) {
    const {msgString, Max_SizeToShow} = this.props
    if (this.state.isOpen) {
      return msgString ;
    }
    if (renderedStringType){
      return (msgString || "").slice(0, Max_SizeToShow);
    }
    return msgString ;
  }

  getRenderedStringList() {
    const { keyName, classRequired, list = [], msgString, noStyle} = this.props;
    const { isOpen } = this.state;
    const renderedStringType = (typeof msgString == 'string');
    const mainList = this.getRenderedItems();
    const renderedString = this.getRenderedString(renderedStringType);

    if (mainList && mainList.length) {
      return (
        <div className={`${classRequired ? "classification-tag-list min-width220" : ''} ${noStyle ? '': 'more-lessDiv'}`}>
          {
            mainList.map((listItem, id) => (
              listItem ?
                <Tooltip key={id} arrow placement="top" title={keyName ? listItem[keyName] : listItem}>
                  <Chip
                    key={id}
                    className="wrap-tags chip-max-width"
                    size="small"
                    label={keyName ? listItem[keyName] : listItem}
                  />
                </Tooltip>
              : '--'
            ))
          }
          {
            list.length > this.props.Max_SizeToShow &&
            <a
              role="button"
              className="showMoreLessButton"
              tabIndex="0"
              onClick={this.toggle}>{isOpen ? 'Show Less' : 'Show More...'}
            </a>
          }
        </div>
      )
    } else if (renderedStringType) {
      return (
        <div>
          {renderedString}
          {
            msgString.length > this.props.Max_SizeToShow &&
            <span>{isOpen ? " " : "..."}
              <b className="showMoreLessText" onClick={this.toggle}>
                {isOpen ? 'Read Less' : 'Read More'}
              </b>
            </span>
          }
        </div>
      )
    }
    return <div>{msgString}</div>
  }

  render() {
    return this.getRenderedStringList();
  }
}

MoreLessComponent.defaultProps={
  Max_SizeToShow:3,
  noStyle: false
}

@observer
class DiagnosticIbox extends Component {
  state = {
    open: true
  }
  get showCount() {
    if (!this.props.showCount) {
      return null;
    }
    if (this.props.countNode) {
      return this.props.countNode;
    }
    return <span className="pull-right m-r-sm paths-count">(<strong>{this.counts}</strong>) {this.props.countText}</span>;
  }
  get counts() {
    if (typeof this.props.count == "number") {
      return this.props.count;
    }
    if (f.isPromise(this.props.count)) {
      return f.models(this.props.count).length;
    }
  }
  handleCollapse = () => {
    const {
      state
    } = this;
    state.open = !state.open;
    this.setState(state);
  }
  render() {
    const {title, path, titleHtml, headerTextColorClass, iboxClassName, children} = this.props;

    return (
      <Card>
        <CardHeader
          title={
            <div className="pointer" onClick={this.handleCollapse}>
              <IconButton aria-label="expand row" size="small">
                {this.state.open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
              </IconButton>
              {titleHtml}
              <Typography component="span" variant="h6" className={`m-l-xs ${headerTextColorClass} ${path ? 'seperator' : ''}`}>{title}</Typography>
              {path && <div className="inline-block left m-l-md">{path}</div>}
              {this.showCount}
            </div>
          }
          titleTypographyProps={{variant: 'body1', component: 'h5'}}
        />
        <Collapse in={this.state.open}>
          <CardContent>{children}</CardContent>
        </Collapse>
      </Card>
    )
  }
}
DiagnosticIbox.defaultProps = {
  title: "",
  path: "",
  showCount: true,
  count: 0,
  countNode: null,
  countText: "",
  iboxClassName: "",
  titleHtml: "",
  headerTextColorClass: 'text-primary'
}

const TopAccess  = observer(function TopAccess({title, data, onClick, colAttr={sm: 6, md: 3}}) {
  return (
    <Grid item {...colAttr}>
      <Ibox className="top-listing-box" title={title}>
        <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')} >
          <div>
            {
              f.models(data).length > 0 ? f.models(data).map((obj, i) => {
                let perCount = (( +obj.value / +obj.total ) * 100).toFixed(2);
                let per = `${perCount < 1 ? 1 : perCount}%`;
                return (
                  <div className="feed-activity-list nomargin-feed" style={{cursor: onClick && 'pointer'}} key={obj.id}
                    onClick={(e) => {
                        onClick && onClick(e, obj.name);
                    }}
                  >
                    <FeedElement obj={obj} percentage={per} />
                  </div>
                )
              }) : <div className="text-center no-data">No Data Available</div>
            }
          </div>
        </Loader>
      </Ibox>
    </Grid>
  )
});

const FeedElement = ({obj, percentage}) => {
  return (
    <div className="feed-element">
      <h4 className="no-margins" title={obj.name}>{obj.name}&nbsp;<small></small></h4>
      <div className="stat-percent w-mx-30 ellipsize" title={obj.value}>{obj.value}</div>
      <div className="progress progress-mini">
        <div style={{width: `${percentage}`}} className="progress-bar"></div>
      </div>
    </div>
  )
}

@observer
class ImportForm extends Component {
  state={error:false, errMsg:'Required'}
  selectedFileForImport;

  constructor(props){
    super(props);
    this.fileJson = createRef();
  }

  getFileExtension = filename =>  {
    return (/[.]/.exec(filename)) ? /[^.]+$/.exec(filename)[0] : undefined;
  }

  handleCancel = () =>{
    this.props.onCancelClick && this.props.onCancelClick();
  }

  validate = () => {
    try {
      let file = this.fileJson?.current?.files[0];

      if (this.props.acceptFormat && this.props.acceptFormat.length) {
        const name = file.name && file.name.toLowerCase();
        const ext = this.getFileExtension(name);
        if(!this.props.acceptFormat.toString().includes(ext)) {
            return false;
        }
      }
      return true;
    } catch(e) {}
    return false;
  }
  checkIfFileAddedOrNot=()=>{
    let isValid = false;
    let file = this.fileJson?.current?.files[0];
    if (!file) {
      this.setState({error:true,errMsg:'Required'})
    } else if (this.validate()) {
      isValid = true;
      this.setState({error:false, errMsg: ''})
    } else {
      this.setState({error:true, errMsg:'Please upload '+this.props.acceptFormat+' type file'})
    }
    return isValid;
  }
  handleInputChange = (e) => {
    if (e.target.files.length && this.validate()) {
      this.selectedFileForImport = this.fileJson?.current?.files[0];
      if (this.props.onClick) {
        this.props.onClick(this.getFormData(), null)
      }
      this.setState({error:false, errMsg:''})
    } else {
      this.selectedFileForImport = '';
      if (this.props.onError) {
        this.props.onError()
      }
      this.setState({error:true, errMsg:'Please upload '+this.props.acceptFormat+' type file'})
    }
  }
  getFormData = () => {
    let isValid = this.checkIfFileAddedOrNot();
    if (isValid) {
      let formData = new FormData();
      formData.append('file', this.selectedFileForImport);
      return formData;
    }
  }
  render() {
    const { showCancelButton, showprogress } = this.props
    return (
      <Grid container spacing={3}>
        <Grid item sm={12}>
          <input
            ref={this.fileJson}
            type="file"
            name="importFileName"
            accept={this.props.acceptFormat}
            placeholder={this.props.acceptFormat ? 'Select '+ this.props.acceptFormat.join(', ').toLowerCase()+' type file' : ''}
            required={true}
            className="form-control"
            onChange={(event) => this.handleInputChange(event)}
          />
          {this.props.acceptFormat.length > 0
            && <p className="m-t-sm text-default">Supported file types are <strong>{this.props.acceptFormat.join(', ').toLowerCase()}</strong></p>}
          {this.state.error 
            && <ValidationMsgField msg={this.state.errMsg} />}
          {showprogress &&
            <Box mt={2} >
              <Box display="flex" justifyContent="center" alignItems="center">
                <CircularProgress size={20} className="m-r-xs" /> Uploading file...
              </Box>
              <Box mt={2} id="delay-show-30s" display="flex" justifyContent="center">
                <InfoOutlinedIcon  fontSize="small" color="primary" className="m-r-xs" /> Please wait, it might take some time to upload file.
              </Box>
            </Box>
          }
          {this.props._vState.uploadInProgress && <LinearProgressWithLabel boxProps={{my: 2}} handleCancel={this.handleCancel} showCancelButton={showCancelButton} value={this.props._vState.uploadPercentage} />}
        </Grid>
      </Grid>
    )
  }
}
ImportForm.defaultProps = {
  acceptFormat: ['.json'],
  _vState: {}
}

ImportForm.propTypes = {
  acceptFormat: PropTypes.array
};

class ExportForm extends Component {

	constructor(props) {
	  super(props)
	  this.state = {
		isAllChecked: true,
		modules: f.models(this.props.cGlobalExport)
	  }
	}
  
  
	handleChange = (checked) => {
	  checked ? this.state.modules = f.models(this.props.cGlobalExport) : this.state.modules = this.state.modules;
	  this.state.isAllChecked = checked
	  let val = this.state.modules.map(item => item.id)
	  this.props.selectedModule(val, checked);
	  this.setState(this.state);
	}
  
	render() {
	  const {cGlobalExport} = this.props;
	  return (
		<Box m={1}>
			<FormGroupSelect2
			  inputColAttr={{ sm: 12, md: 12 }}
			  label={"Modules"}
			  multiple={true}
			  valueKey={'id'}
			  labelKey={'label'}
			  required={true}
			  disabled={this.state.isAllChecked}
			  data={f.models(cGlobalExport)}
			  value={this.state.modules}
			  onChange={(val) => {
				this.state.modules = val;
				this.props.selectedModule(val.split(','), this.state.isAllChecked);
				this.setState(this.state)
			  }}
			  errMsg={this.state.modules ? '' : 'Required!'}
			>
			</FormGroupSelect2>
			<Grid item sm={3} md={2} className="m-t-sm">
			  <Checkbox checked={this.state.isAllChecked} labelText='All' onChange={e => {
				let isChecked = e.target.checked;
				this.handleChange(isChecked)
			  }} />
			</Grid>
		</Box>
	  )
	}
}

class ResourceLookupSelect2 extends Component {
  regexPattern = "";
  constructor(props={}) {
    super(props);
    if (props.regexPattern) {
      this.regexPattern = props.regexPattern;
    }
  }
  componentDidMount() {
    this.lookupResource = this.props.lookupResource;
    this.lookupResource.appCode = this.props.app && this.props.app.uniqueCode;
    this.getLookUpData();
  }

  getValidString = (value) => {
    if (!value) {
        return '';
    }
    return value.replace(this.regexPattern, "");
  }
  getNameValue = (res) => {
    let list = [];
    if (res && this.lookupResource.userInput) {
      res = [this.lookupResource.userInput, ...res];
      res = uniq(res);

      list = res.map((value) => {
        const obj = {label: value, value};
        if (this.props.showTitle) {
          obj.title = value;
        }
        return obj;
      });
    }

    return list;
  }

  getAsyncCallbackOptions = (res) => {
    return this.getNameValue(res)
  }

  searchResource = (searchFor, callback) => {
    allStores.generalStore.lookupResource(this.getLookUpData(searchFor), {
        serviceName: this.props.serviceName
    }).then((res) => callback(this.getAsyncCallbackOptions(res.result)), () => callback(this.getAsyncCallbackOptions()))
  }
  loadOptions = (searchFor="", callback) => {
    if(isArray(searchFor) || (searchFor && searchFor.indexOf(',') > -1)) {
      return callback(this.getAsyncCallbackOptions());
    }
    let debounce = isDebounce(() => this.searchResource(searchFor, callback), 100);
    this.lookupResource.userInput = this.getValidString(searchFor);
    if (this.lookupResource.userInput) {
      debounce();
    } else {
      callback(this.getAsyncCallbackOptions());
    }
  }
  componentDidUpdate(prevProps) { 
    if(prevProps?.app?.uniqueCode!== this.props?.app?.uniqueCode){
      this.lookupResource.appCode = this.props.app && this.props.app.uniqueCode;
    }
    this.getLookUpData(); 
  }

  render() {
    const {serviceName, resourceName, lookupResource, app, ...props} = this.props;
    return (
      <FormGroupSelect2
        loadOptions={this.loadOptions}
        allowCreate={true}
        {...props}
      />
    )
  }
}

ResourceLookupSelect2.defaultProps = {
  app: {},
  lookupResource: new MLookupResource()
}

class HdfsResourceLookupSelect2 extends ResourceLookupSelect2 {
  getSelectedResource = (userInput) => {
    if (this.props.value || userInput) {
      if (isArray(this.props.value)) {
        return this.props.value;
      }
      if (typeof this.props.value == "string" || typeof userInput == "string") {
        const val = this.props.value || userInput;
        if (val) {
          return val.split(',');
        }
      }
    }
    return [];
  }
  getLookUpData = (userInput) => {
    let path = this.getSelectedResource(userInput);
    let rName = RESOURCE_SERVICE?.HDFS.resource.PATH.name;
    Object.assign(this.lookupResource, {
      resourceName: rName,
      resources: {
          [rName]: path
      }
    })
    return this.lookupResource;
  }
}
HdfsResourceLookupSelect2.defaultProps = {
serviceName: RESOURCE_SERVICE?.HDFS.name,
regexPattern: RESOURCE_SERVICE?.HDFS.pattern
}


class HiveResourceLookupSelect2 extends ResourceLookupSelect2 {
  regexPattern = RESOURCE_SERVICE?.HIVE.pattern;
  getSelectedResource = (userInput) => {
    if (this.props.value || userInput) {
      if (isArray(this.props.value)) {
        return this.props.value;
      }
      if (isArray(userInput)) {
        return userInput;
      }
      if (typeof this.props.value == "string" || typeof userInput == "string") {
        const val = this.props.value || userInput;
        if (val) {
          return val.split(',');
        }
      }
    }
    return [];
  }
  getResources = (userInput) => {
    this.props.lookupResource.resources[this.props.resourceName] = this.getSelectedResource(userInput);
    return this.props.lookupResource.resources;
  }
  getLookUpData = (userInput) => {
    if (this.props.projectId) {
      Object.assign(this.lookupResource.resources, this.props.projectId);
    }
    this.lookupResource.resourceName = this.props.resourceName
    this.lookupResource.resources[this.props.resourceName] = this.getSelectedResource(userInput);

    return this.lookupResource;
  }
}
HiveResourceLookupSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.HIVE.name,
  resourceName: RESOURCE_SERVICE?.HIVE.resource.DATABASE.name
}

class AWSS3ResourceLookupSelect2 extends ResourceLookupSelect2 {
  regexPattern = RESOURCE_SERVICE?.AWSS3.pattern;
  getSelectedResource = (userInput) => {
    if (this.props.value || userInput) {
      if (isArray(this.props.value)) {
        return this.props.value;
      }
      if (typeof this.props.value == "string" || typeof userInput == "string") {
        const val = this.props.value || userInput;
        if (val) {
          return val.split(',');
        }
      }
    }
    return [];
  }
  getLookUpData = (userInput) => {
    let path = this.getSelectedResource(userInput);
    let rName = RESOURCE_SERVICE?.AWSS3.resource.PATH.name;
    Object.assign(this.lookupResource, {
      resourceName: rName,
      resources: {
          [rName]: path
      }
    })
    return this.lookupResource;
  }
}
AWSS3ResourceLookupSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.AWSS3.name
}
class AzureAdlsResourceLookupSelect2 extends HdfsResourceLookupSelect2 {}
AzureAdlsResourceLookupSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.AZURE_ADLS.name
}
class GCSResourceLookupSelect2 extends HdfsResourceLookupSelect2 {
  getSelectedResource = userInput => {  
    if (this.props.value || userInput) {  
      if (isArray(this.props.value)) {  
        return this.props.value;  
      } 
      if (isArray(userInput)) { 
        return userInput; 
      } 
      if (this.props.value && typeof this.props.value == "string") {  
        return this.props.value.split(','); 
      } 
      if (userInput && typeof userInput == "string") {  
        return userInput.split(',');; 
      } 
    } 
    return [];  
  } 
  getLookUpData = (userInput) => {  
    if (this.props.projectId) { 
      Object.assign(this.lookupResource.resources, this.props.projectId)  
    } 
    this.lookupResource.resourceName = this.props.resourceName  
    this.lookupResource.resources[this.props.resourceName] = this.getSelectedResource(userInput); 
    return this.lookupResource; 
  }
}
GCSResourceLookupSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.GOOGLE_CLOUD_STORAGE.name,  
  resourceName: RESOURCE_SERVICE?.GOOGLE_CLOUD_STORAGE.resource.PATH.name
}

class HBaseResourceLookupSelect2 extends HiveResourceLookupSelect2 {
}
HBaseResourceLookupSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.HBASE.name,
  resourceName: RESOURCE_SERVICE?.HBASE.resource.DATABASE.name
}

class CassandraResourceLookupSelect2 extends HiveResourceLookupSelect2 {
}
CassandraResourceLookupSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.CASSANDRA.name,
  resourceName: RESOURCE_SERVICE?.CASSANDRA.resource.DATABASE.name
}
class AWSDynamoDBLookupSelect2 extends HiveResourceLookupSelect2 {
}
AWSDynamoDBLookupSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.AWS_DYNAMO_DB.name,
  resourceName: RESOURCE_SERVICE?.AWS_DYNAMO_DB.resource.DATABASE.name
}

class JDBCSelect2 extends HiveResourceLookupSelect2 {
}
JDBCSelect2.defaultProps = {
  serviceName: RESOURCE_SERVICE?.JDBC.name,
  resourceName: RESOURCE_SERVICE?.JDBC.resource.DATABASE.name
}


const tourStyles = {
  paper: {
    overflow: 'initial',
    transition: 'all 0.2s linear !important'
  }
}
class TourManager2Styles extends Component {
  state = {
      showTourPopover: false,
      overlayConfig: {
          target: null,
          position: null,
          title: null,
          desc: null
      },
      prevDisabled: true,
      nextDisabled: false,
      loading: false
  }

  currentStepNode = null;
  all = null;
  overlay = null;
  stepContainer = null;
  timeoutToWaitForEle = null;
  observerForTour = null;

  constructor(props){
      super(props);
      this.disposeReaction = reaction(
        () => tourManagerUtil.triggerTourStatus,
        () => {
          if ( tourManagerUtil.triggerTourStatus) {
            this.setDataAndStartTour(tourManagerUtil.triggerTourStatus, tourManagerUtil.getTourStartStep);
          }
        }
      );

      this.disposeReaction1 = reaction(
        () => tourManagerUtil.isStepChanged,
        () => {
          if (tourManagerUtil.isStepChanged) {
            this.resetTourData();
          }
        }
      );
      this.tourManagerRef = createRef()
  }

  resetTourData = () => {
    this.all = tourManagerUtil.steps;
    tourManagerUtil.changeAcknowledged();
  }
  
  setDataAndStartTour = (triggerTourStatus, startTourStep) => {
    tourManagerUtil.triggerTourAcknowledged();
    this.all = tourManagerUtil.steps.slice();
    this.startTour(startTourStep)
  }

  componentWillUnmount() {
    this.tourManagerRef = null;
    this.currentStepNode = null;
    this.all = null;
    this.toggleOverlayAndContainer(false);

    // dispose the reaction method
    if (this.disposeReaction) {
      this.disposeReaction();
    }
    if (this.disposeReaction1) {
      this.disposeReaction1();
    }
    delete this.disposeReaction;
    delete this.disposeReaction1;
  }
  
  setLeftRight = (rect, position) => {
    const {left, right, top, bottom} = rect;
    switch (position) {
      case "right":
        this.left = right + 10 ;
        this.top = top ;
        break;
      case "left":
        this.left = left - 20;
        this.top = top;
        break;
      case "top":
        this.left = left;
        this.top = top - 20;
        break;
      case "bottom":
        this.left = left;
        this.top = bottom + 10;
        break;
    }
    return origin;
  }
  waitForElm = (selector, alternateSelector = null, wait = 15000)  => {
    return new Promise((resolve) => {
      if (document.querySelector(selector)) {
        return resolve(document.querySelector(selector));
      }
      if (document.querySelector(alternateSelector)) {
        return resolve(document.querySelector(alternateSelector));
      }
      this.timeoutToWaitForEle = setTimeout(
          () => {
            this.observerForTour.disconnect();
            resolve(null);
          },
          wait
      );
      this.observerForTour = new MutationObserver(mutations => {
        const resolver = document.querySelector(selector)
        const alternateResolver = document.querySelector(alternateSelector)
        if (resolver || (alternateSelector && alternateResolver)) {
          clearTimeout(this.timeoutToWaitForEle);
          this.timeoutToWaitForEle = null
          resolve(resolver || alternateResolver); // resolve only that selector which is found using querySelector
          this.observerForTour.disconnect();
        }
      });

      this.observerForTour.observe(document.body, {
        childList: true,
        subtree: true
      });
    });
  }
  
  componentDidUpdate(prevProps, prevState) {
    if (!prevState.showTourPopover && this.state.showTourPopover) {
      this.setState({loading: false})
    }
  }
  asyncScrollIntoView = (target) => {
    return new Promise ((resolve) => {
      target.scrollIntoView()
      setTimeout(() => {
        resolve(true)
      }, 1000)
    })
  }
  getTourStepData = async () => {
    this.setState({loading: true})
    if (this.currentStepNode) {
      this.setState({showTourPopover : false})
      // currentStepNode can be grandchild of container as well as it can be child of other parent nodes
      // so remove using .parentNode
      if (document.querySelector("#tour-step-container").contains(this.currentStepNode)) {
        this.currentStepNode.parentNode.removeChild(this.currentStepNode)
      }
      // document.querySelector("#tour-step-container").removeChild(this.currentStepNode);
      this.currentStepNode = null;
    }
    const currentInfo = this.all[this.currentStep - 1] || {};
    let target = document.querySelector(`#${currentInfo.id}`);
    if (!target && currentInfo.alternateId) { // if first target not found then check if second id is present for different target 
      target = document.querySelector(`#${currentInfo.alternateId}`);
    }
    if(!target){
      target = await this.waitForElm(`#${currentInfo.id}`, `#${currentInfo.alternateId}`);
      if (!target && currentInfo.alternateId) { // if first target not found then check for second id and try to find that target
        target = document.querySelector(`#${currentInfo.alternateId}`);
      }
      if(!target){
        this.gotoStep(this.currentStep + 1)
        return
      }
    }
    if (currentInfo.scrollToView) {
      await this.asyncScrollIntoView(target)
    }
    const rect = target.getBoundingClientRect();
    this.setLeftRight(rect, currentInfo.position);
    this.currentStepNode = document.createElement("div");
    const targetClone = target.cloneNode(true);
    if (window.innerHeight - (rect.height + rect.top) < 0) {
      targetClone.setAttribute("style", `height: ${rect.height}px`);
    }
    this.currentStepNode.appendChild(targetClone);
    this.currentStepNode.setAttribute(
      "style",
      `
       height: ${rect.height + 10}px;
       width: ${rect.width + 10}px;
       top: ${rect.top - 5}px;
       left: ${rect.left - 5}px;
       text-align: left;padding: 4px;
       border-radius: 5px;
       text-transform:uppercase
      `);
    this.currentStepNode.setAttribute("class", "tour-step");
    //target.hide = true;
    if (document.querySelector("#tour-step-container")) {
      document.querySelector("#tour-step-container").appendChild(this.currentStepNode);
    }
    const overlayConfig = {
      target: this.currentStepNode,
      position: currentInfo.position,
      title: currentInfo.title,
      desc: currentInfo.desc
    }
    
    const prevDisabled = this.currentStep - 1 == 0;
    const nextDisabled = this.currentStep === this.all.length;
    return {
      overlayConfig,
      prevDisabled,
      nextDisabled
    }
  }

  gotoStep = (step) => {
    if (this.timeoutToWaitForEle) {
      clearTimeout(this.timeoutToWaitForEle);
      this.observerForTour.disconnect();
      this.timeoutToWaitForEle = null;
    }
    if (step === this.currentStep) {
      return;
    }
    const forWard = step > this.currentStep ? true : false;
    this.currentStep = step;
    const currInfo = this.all[this.currentStep - 1];
    const actionAfterUpdate = async () =>{
      if (!forWard && currInfo && currInfo.prevStep) {
        this.currentStep = currInfo.prevStep - 1;
      }
      let data = await this.getTourStepData();
      this.setState({ ...data, loading: false, showTourPopover: true })
    }

    if (!forWard && currInfo && currInfo.onPrev) {
      currInfo.onPrev(
        currInfo.pauseTourTillUpdate ? actionAfterUpdate : null
      );
    }
    if (forWard && currInfo && currInfo.onNext) {
      currInfo.onNext(
        currInfo.pauseTourTillUpdate ? actionAfterUpdate : null
      );
    }
    //this is mandatory if you want to accept the changes on UI
    if (!currInfo.pauseTourTillUpdate){
      actionAfterUpdate()
    }
  }

  onExitClick = () => {
    this.all = null;
    if (this.currentStepNode) {
      if (document.querySelector("#tour-step-container")) {
        document.querySelector("#tour-step-container").removeChild(this.currentStepNode); 
      }
      this.currentStepNode = null;
    }
    this.toggleOverlayAndContainer(false);
    this.setState({showTourPopover : false, nextDisabled: false, prevDisabled: true},tourManagerUtil.exitTour)
  }

  toggleOverlayAndContainer = (toggle) => {
    if (!toggle) {
      if (this.overlay) {
        document.querySelector("#base-container").removeChild(this.overlay);
        this.overlay = null;
      }
      if (this.stepContainer) {
        document.querySelector("#base-container").removeChild(this.stepContainer);
        this.stepContainer = null;
      }
      document.querySelector("body").classList.remove("tour-overflow-hidden");
    }else {
      document.querySelector("body").classList.add("tour-overflow-hidden");
      if (!this.overlay) {
        this.overlay = document.createElement("div");
        this.overlay.setAttribute("class", "tour-overlay");
        document.querySelector("#base-container").appendChild(this.overlay);
      }
      if (!this.stepContainer) {
        this.stepContainer = document.createElement("div");
        this.stepContainer.setAttribute("id", "tour-step-container");
        document.querySelector("#base-container").appendChild(this.stepContainer);
      }
    }
  }

  startTour =  async (currentStep) => {
      this.setState({loading: true, prevDisabled: currentStep ? false : true})
      if (this.state.showTourPopover) { return; }
      window.scroll({
        top: 0,
        behavior: 'smooth'
      })
      this.toggleOverlayAndContainer(true);
      console.log('currentStep', currentStep)
      this.currentStep = currentStep || 1;
      let data = await this.getTourStepData()
      this.setState({
        showTourPopover:true,
        ...data
      });
  }

  getButtonText = () => {
      if( !this.all || !this.currentStep ) {return "Exit";}
      if(this.all.length-1 === this.currentStep) {return "Finish"}
      return "Exit"
  }

  getOrigin = (position) => {
    const origin = {      
     horizontal : 'right',
     vertical : 'center'
    };
    switch (position) {
      case "right":
        origin.horizontal = 'right';
        origin.vertical = 'center';
        break;
      case "left":
        origin.horizontal = 'left';
        origin.vertical = 'center';
        break;
      case "top":
        origin.horizontal = 'center';
        origin.vertical = 'top';
        break;
      case "bottom":
        origin.horizontal = 'center';
        origin.vertical = 'bottom';
        break;
    }
    return origin;
  }

  getTransformOrigin = () => {
    const { overlayConfig : {position = "right"}} = this.state;
    let transformPosition = "";
    switch (position) {
      case "right":
        transformPosition = "left";
      break;
      case "left":
        transformPosition = "right";
      break;
      case "top":
        transformPosition = "bottom";
        break;
      case "bottom":
        transformPosition = "top";
        break;
    }
    return this.getOrigin(transformPosition);
  }

  onLoaderExitClick = () => {
    this.setState({loading: false})
    this.onExitClick()
  }

  render() {
      const { overlayConfig, prevDisabled, nextDisabled, loading } = this.state;
      const {top = 0, left = 0, currentStep, all, gotoStep, onExitClick} = this;
      const {classes} = this.props;

      const loaderButtonsOptions = { prevDisabled, nextDisabled, currentStep, all }
      const loaderButtonsCallbacks = { gotoStep, onExitClick }

      return (
        <div ref={this.tourManagerRef}>
          <Popover
            anchorReference="anchorPosition"
            open={this.state.showTourPopover}
            anchorEl={overlayConfig.target}
            anchorPosition={{top, left}}
            transformOrigin={this.getTransformOrigin()}
            id="popover-contained"
            className="tour-box" 
            elevation={16}
            classes={{paper: classes.paper}}
          >
            <Container>
            <Box maxWidth="350px"  position="relative">
            <span className="tour-chip">{currentStep}</span>
            <Box display="flex" p={3} pb={0}>
              <Typography variant="body1">
                {overlayConfig.title}
              </Typography>
              <Box position="absolute" top={0} right={0}>
                <IconButton color="primary" onClick={this.onExitClick}>
                  <ClearIcon fontSize="small" />
                </IconButton>
              </Box>
            </Box>
              <Box display="flex" p={3} pb={0}>
                <Typography variant="body2">
                    {overlayConfig.desc}
                  </Typography>
              </Box>  
                <LoaderButtons
                  options={loaderButtonsOptions}
                  callbacks={loaderButtonsCallbacks}
                />
              </Box>
            </Container>
          </Popover>

          <LoaderPopover
            showPopover={loading}
            classes={classes}
            onExitClick={this.onLoaderExitClick}
            loaderButtonsOptions={loaderButtonsOptions}
            loaderButtonsCallbacks={loaderButtonsCallbacks}
          />
        </div>
      );
  }
}

class LoaderButtons extends Component {

  render () {

    const { prevDisabled, nextDisabled, currentStep, all } = this.props.options
    const { gotoStep, onExitClick } = this.props.callbacks

    return (
      <Box display="flex" justifyContent="space-between" alignItems="center" p={2}>
        <Box>
          <IconButton size="small" color="primary" disabled={prevDisabled} onClick={() => gotoStep(currentStep - 1)}>
            <ArrowBackIcon  fontSize="small" />
          </IconButton>
        </Box>
        <Box display="flex" flexWrap="wrap" className="tour-btn-container">
          {all && all.map((el, i) => (
            <button key={i} className={`tour-btn ${i + 1 === currentStep ? 'active not-allowed': ''}`}  onClick={() => gotoStep(i + 1)} />
          ))}
        </Box>
        <Box>
          {!nextDisabled ?
            <IconButton size='small' color="primary" disabled={nextDisabled} onClick={() => gotoStep(currentStep + 1)}>
              <ArrowForwardIcon fontSize="small" />
            </IconButton>
          : <Button size="small" color="primary" variant="contained" onClick={onExitClick}>End</Button>
          }
        </Box>
      </Box>
    )
  }
}

const LoaderPopover = observer(({showPopover, classes, onExitClick, loaderButtonsOptions, loaderButtonsCallbacks}) => {
  return (
    <Popover
      anchorReference="anchorEl"
      open={showPopover}
      anchorEl={"body"}
      anchorOrigin={{vertical: 'center', horizontal: 'center' }}
      transformOrigin={{vertical: 'center', horizontal: 'center'}}
      id="loader-popover"
      className="tour-box"
      elevation={16}
      classes={{paper: classes.paper}}
    >
      <Container>
        <Box maxWidth="350px" position="relative" style={{width: "398px", height: "228px"}}>
          <Box display="flex" p={3} pb={0}>
            <Typography variant="body1">
              Tour - Loading
            </Typography>
            <Box position="absolute" top={0} right={0}>
              <IconButton color="primary" onClick={() => onExitClick()}>
                <ClearIcon fontSize="small" />
              </IconButton>
            </Box>
          </Box>
          <Box display="flex" p={3} pb={0} style={{height: "calc(100% - 120px)", alignItems: "center"}}>
            <Typography variant="body2" style={{margin: "0 auto"}}>
              <LoopIcon className="tour-loader-icon" color="primary" />
            </Typography>
          </Box>
            <LoaderButtons
              options={loaderButtonsOptions}
              callbacks={loaderButtonsCallbacks}
            />
        </Box>
      </Container>
    </Popover>
  )
})

// const TourManager2 = withStyles(tourStyles)(TourManager)
const TourManager2 = withStyles(tourStyles)(TourManager2Styles)

const PopperMenu = ({buttonType, buttonProps, isButtonContained=true, label, popperProps, menuListProps, menuItemProps, menuOptions = [], renderCustomMenus}) => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleKeyPress = () => {
    event.preventDefault();
  }

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMenuItemClick = (option, ...props) => {
    if (option.onClick) {
      option.onClick(option, ...props)
    }
    handleClose();
  }

  let popperLabel = null;
  if (buttonType == 'Button') {
    popperLabel = (
      <Button
        aria-controls={open ? 'menu-list-grow' : undefined}
        aria-haspopup="true"
        variant={isButtonContained ? "contained" : null}
        color="primary"
        size="small"
        {...buttonProps}
        onClick={handleClick}
      > {label}
      </Button>
    )
  } else if (buttonType == 'IconButton') {
    popperLabel = (
      <IconButton aria-label="more" {...buttonProps} onClick={handleClick}>
        {label}
      </IconButton>
    )
  } else {
    popperLabel = (
      <span onClick={handleClick}>
        {label}
      </span>
    )
  }

  return (
    <Fragment>
      {popperLabel}
      <Popper
        role={undefined}
        transition
        open={open}
        anchorEl={anchorEl}
        placement="bottom-end"
        {...popperProps}
        style={{zIndex: 1300}}
      >
        {
          ({ TransitionProps, placement }) => (
            <Grow
              {...TransitionProps}
              style={{ transformOrigin: placement === 'bottom' ? 'center top' : 'center bottom' }}
            >
              <Paper>
                <ClickAwayListener onClickAway={handleClose}>
                  <MenuList
                    className="mui-cardMenu"
                    autoFocusItem={Boolean(open)}
                    id="menu-list-grow"
                    onKeyPress={handleKeyPress}
                    onKeyDown={handleKeyPress}
                    {...menuListProps}>
                    {
                      renderCustomMenus
                      ? renderCustomMenus(handleClose)
                      : menuOptions.map(option => {
                          const {label, ...props} = option;
                          return (
                            <MenuItem key={label} {...menuItemProps} {...props}
                              onClick={(...props) => handleMenuItemClick(option, ...props)}>
                              {label}
                            </MenuItem>
                          )
                        }
                      )
                    }
                  </MenuList>
                </ClickAwayListener>
              </Paper>
            </Grow>
          )
        }
      </Popper>
    </Fragment>
  )
}
PopperMenu.defaultProps = {
  buttonProps: {},
  label: <MoreVertIcon />,
  popperProps: {},
  menuOptions: {},
  menuListProps: {},
  menuItemProps: {},
  renderCustomMenus: null
}

const TabPanel = (props) => {
  const { children, value, index, renderAll=true, ...other } = props;

  if (renderAll || value === index) {
    return (
      <Box
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        p={2}
        {...other}
      >
        {children}
      </Box>
    )
  }
  return null;
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.any.isRequired,
  value: PropTypes.any.isRequired
};

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1
  },
  margin: {
    margin: theme.spacing(1)
  },
  progressLabel: {
    position: "absolute",
    width: "100%",
    height: "100%",
    zIndex: 1,
    maxHeight: "20px",
    textAlign: "center",
    display: "flex",
    alignItems: "center",
    "& span": {
      width: "100%"
    }
  },
  progressBar: {
    backgroundColor: '#f3f3f3'
  }
}));

const CustomProgressBar = observer((props) => {
  const {value, label} = props;
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <Grid container spacing={1} justify="space-between">
        <Grid item xs={12} spacing={0}>
          <div className={classes.progressLabel}>
          {label && (
            <Typography component="span" style={{color: (value > 50 ? 'white' : 'inherit')}}>
            {label}
          </Typography>
          )}
          </div>
          <LinearProgress
            value={value}
            className={classes.progressBar}
            variant="determinate"
            style={{ height: "20px" }}
            {...props}
          />
        </Grid>
      </Grid>
    </div>
  );
})


const usePopoverStyles = makeStyles((theme) => ({
  popover: {
    pointerEvents: 'none',
  },
  paper: {
    padding: theme.spacing(1),
  },
}));
const CustomPopover = ({open, getTarget, close, popoverContent, anchorOrigin={vertical: 'bottom', horizontal: 'center' }, transformOrigin={ vertical: 'top', horizontal: 'center'}, trigger=['hover'], className, ...props}) => {
  const classes = usePopoverStyles();
  const _className = clsx(trigger.includes("hover") ? classes.popover : null, className);
    return(
      <Popover
        id="mouse-over-popover"
        className={_className}
        classes={{ paper: classes.paper }}
        open={open}
        anchorEl={getTarget}
        anchorOrigin={anchorOrigin}
        transformOrigin={transformOrigin}
        onClose={close}
        disableRestoreFocus
        {...props}
      >
        {popoverContent}
      </Popover>
    );
}

const SkeletonByCount = ({count, props, width = [],height=[]}) => {
  const skel= [];
  for (let index = 0; index < count; index++) {
    skel.push(
      <Skeleton 
        key={index} 
        width={width[index] || props.width} 
        height={height[index] || props.height} 
        {...props} 
      />)    
  }
  return skel;
}

const PrivaceraLoader=()=>{
  return(
    <div className="loader-container">
      <div className="loader-inner">
        <svg width="261px" height="60px" viewBox="0 0 96 22" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M16.2 6.28998C16.72 5.27998 17.77 4.66001 18.9 4.69001C20.1 4.69001 21.69 5.33 21.69 6.5C21.72 7.08 21.29 7.60999 20.71 7.66999C20.68 7.66999 20.65 7.66999 20.62 7.66999C20.31 7.66999 20.01 7.55002 19.76 7.33002C19.39 7.02002 18.93 6.84 18.44 6.87C16.97 6.87 16.2 7.94002 16.2 9.33002V14.46C16.2 15.5 15.99 16.03 15.06 16.03C14.2 16.03 13.99 15.51 13.99 14.4V6.16999C13.99 5.42999 14.3 4.96997 14.97 4.96997C15.86 4.96997 16.05 5.36998 16.2 6.28998Z" fill="#2D4ADA"/>
          <path d="M25.96 1.84003C25.99 2.61003 25.38 3.25003 24.61 3.28003C23.75 3.28003 23.2 2.76003 23.2 1.84003C23.17 1.10003 23.75 0.490022 24.49 0.460022C24.52 0.460022 24.58 0.460022 24.61 0.460022C25.35 0.520022 25.93 1.14003 25.96 1.84003ZM25.75 14.89C25.75 15.69 25.38 16.09 24.58 16.09C23.81 16.09 23.44 15.69 23.44 14.89V6.20001C23.44 5.34001 23.78 4.94 24.55 4.94C25.32 4.94 25.72 5.34001 25.72 6.20001V14.89H25.75Z" fill="#2D4ADA"/>
          <path d="M32.62 12.89L35.44 5.77002C35.69 5.16002 36.08 4.90997 36.58 4.90997C37.16 4.90997 37.65 5.39998 37.65 5.97998C37.65 6.18998 37.59 6.41003 37.5 6.59003L33.91 15.15C33.63 15.79 33.3 16.1 32.65 16.1C32.04 16.1 31.67 15.82 31.39 15.15L27.77 6.62C27.68 6.44 27.65 6.21998 27.62 6.03998C27.59 5.42998 28.08 4.93002 28.66 4.90002C28.66 4.90002 28.66 4.90002 28.69 4.90002C29.15 4.90002 29.55 5.17998 29.83 5.78998L32.62 12.89Z" fill="#2D4ADA"/>
          <path d="M48.77 4.82001C49.51 4.82001 49.88 5.21999 49.88 6.04999V14.71C49.88 15.66 49.63 16.12 48.81 16.12C48.1 16.12 47.74 15.6 47.64 14.43C47.09 15.47 45.58 16.18 44.08 16.18C40.95 16.18 38.77 13.66 38.77 10.44C38.77 7.16 40.95 4.66998 44.08 4.66998C45.61 4.66998 47.09 5.31001 47.67 6.45001C47.73 5.62001 47.94 4.82001 48.77 4.82001ZM41.03 10.44C41.03 12.4 42.38 13.94 44.31 13.94C46.21 13.94 47.59 12.41 47.59 10.44C47.59 8.57 46.24 6.94 44.31 6.94C42.38 6.94 41.03 8.57 41.03 10.44Z" fill="#2D4ADA"/>
          <path d="M57.21 16.21C54.05 16.24 51.47 13.72 51.44 10.56C51.44 10.53 51.44 10.47 51.44 10.44C51.38 7.30999 53.9 4.69997 57.06 4.66997C57.12 4.66997 57.15 4.66997 57.21 4.66997C58.5 4.63997 59.76 5.03998 60.77 5.80998C61.17 6.05998 61.45 6.51997 61.45 6.97997C61.45 7.55997 60.96 8.04997 60.38 8.04997H60.35C60.01 8.01997 59.71 7.89998 59.43 7.67998C58.82 7.21998 58.05 6.93999 57.25 6.93999C55.32 6.93999 53.78 8.50999 53.78 10.44C53.78 12.37 55.35 13.91 57.28 13.91C58.2 13.91 59.06 13.6 59.74 12.99C59.99 12.74 60.32 12.59 60.69 12.56C61.27 12.56 61.76 13.05 61.76 13.63V13.66C61.73 14.03 61.58 14.37 61.3 14.64C60.4 15.63 58.84 16.21 57.21 16.21Z" fill="#2D4ADA"/>
          <path d="M65.44 10.81C65.72 12.68 66.79 14 68.94 14C69.86 14.03 70.75 13.69 71.46 13.08C71.71 12.8 72.07 12.68 72.41 12.68C72.99 12.68 73.48 13.17 73.48 13.75C73.48 14.82 71.58 16.21 68.88 16.21C65.72 16.21 63.17 13.66 63.17 10.53C63.17 10.5 63.17 10.5 63.17 10.47C63.11 7.33997 65.63 4.76001 68.76 4.70001C68.79 4.70001 68.85 4.70001 68.88 4.70001C72.16 4.70001 74.25 7.24999 74.25 9.29999C74.25 10.28 73.64 10.83 72.53 10.83H65.44V10.81V10.81ZM71.95 9.06C71.67 7.68 70.48 6.84998 68.88 6.84998C67.35 6.84998 65.99 7.71 65.56 9.06H71.95Z" fill="#2D4ADA"/>
          <path d="M78.18 6.28998C78.7 5.27998 79.75 4.66001 80.88 4.69001C82.08 4.69001 83.67 5.33 83.67 6.5C83.7 7.08 83.27 7.60999 82.69 7.66999C82.66 7.66999 82.63 7.66999 82.6 7.66999C82.29 7.66999 81.99 7.55002 81.74 7.33002C81.37 7.02002 80.91 6.84 80.42 6.87C78.95 6.87 78.18 7.94002 78.18 9.33002V14.46C78.18 15.5 77.97 16.03 77.04 16.03C76.18 16.03 75.97 15.51 75.97 14.4V6.16999C75.97 5.42999 76.28 4.96997 76.95 4.96997C77.81 4.96997 77.99 5.36998 78.18 6.28998Z" fill="#2D4ADA"/>
          <path d="M94.36 4.82001C95.1 4.82001 95.47 5.21999 95.47 6.04999V14.71C95.47 15.66 95.22 16.12 94.4 16.12C93.69 16.12 93.33 15.6 93.23 14.43C92.68 15.47 91.17 16.18 89.67 16.18C86.54 16.18 84.36 13.66 84.36 10.44C84.36 7.16 86.54 4.66998 89.67 4.66998C91.2 4.66998 92.68 5.31001 93.26 6.45001C93.31 5.62001 93.53 4.82001 94.36 4.82001ZM86.62 10.44C86.62 12.4 87.97 13.94 89.9 13.94C91.83 13.94 93.18 12.41 93.18 10.44C93.18 8.57 91.83 6.94 89.9 6.94C87.97 6.94 86.62 8.57 86.62 10.44Z" fill="#2D4ADA"/>
          <path d="M11.75 10.44C11.75 13.76 9.57001 16.24 6.35001 16.24H5.61001C4.97001 16.24 4.47001 15.72 4.47001 15.1C4.47001 14.46 4.99001 13.96 5.61001 13.96H6.10001C8.03001 13.96 9.42001 12.36 9.42001 10.46C9.42001 8.50002 8.04001 6.92999 6.10001 6.92999H1.43001C0.850008 6.92999 0.360009 6.49998 0.290009 5.91998C0.290009 5.88998 0.290009 5.86001 0.290009 5.83001C0.290009 5.19001 0.810008 4.69 1.43001 4.69H6.03001C6.15001 4.69 6.24001 4.69 6.37001 4.69C9.54001 4.67 11.75 7.18 11.75 10.44Z" fill="#2D4ADA"/>
          <path d="M6.41002 9.66998C6.26002 9.57998 6.07002 9.54999 5.92002 9.54999H1.44002C0.830018 9.54999 0.300018 10.04 0.300018 10.69V20.82C0.300018 21.43 0.820018 21.96 1.44002 21.96C2.05002 21.96 2.58002 21.44 2.58002 20.82V11.86H5.93002C6.57002 11.86 7.07002 11.34 7.07002 10.72C7.05002 10.25 6.81002 9.85998 6.41002 9.66998Z" fill="#FF4D01"/>
        </svg>
        <LinearProgress className="m-t-sm" />
      </div>
    </div>
  )
}

const getSkeleton=type=>{
  switch(type) {
    case 'SINGLE_FAT_LOADER' : return (<Skeleton animation="wave" variant="rect" height={70} width="100%" />);

    case 'SINGLE_FAT_LOADER2': return (<Skeleton animation="wave" variant="rect" height={300} width="100%" />);

    case 'SINGLE_SLIM_LOADER1' : return (
          <Skeleton animation="wave" variant="text" width="60px" height={38} />
    );
    
    case 'TWO_SLIM_LOADER' : return (
        <Box p={1}>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
        </Box>);
  
    case 'TWO_SLIM_LOADER2' : return (
        <Box p={1}>
            <Skeleton animation="wave" variant="text" width="33%" height={40} />
            <Skeleton animation="wave" variant="text" width="33%" height={30} />
        </Box>);

    case 'TWO_SLIM_LOADER3': return (
      <Paper>
        <Box px={2} py={4}>
          {SkeletonByCount({count: 2, props: {animation: "wave", variant:"text" ,width:"100%", height:20}})}
        </Box>
      </Paper>
    );

    case 'LOADER_WITH_WHITE_BG' : return (
                <Paper>
                    <Box px={2} py={6}>
                        <Skeleton animation="wave" variant="text" width="100%"/>
                        <Skeleton animation="wave" variant="text" width="100%"/>
                    </Box>
                </Paper>
            );
      
    case 'THREE_SLIM_LOADER' : return (
        <Box p={1}>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
        </Box>
        );

    case 'THREE_SLIM_LOADER2': return (
      <Box pt={2}>
      <Skeleton animation="wave" variant="text" height={40} width="20%" />
      <Box pb={1}/>
        <Paper>
          <Box px={2} py={6}>
          {SkeletonByCount({count: 3, props: {animation: "wave", variant:"text" ,width:"100%", height:25}})}
          </Box>
        </Paper>
      </Box>
    );

    case 'TEXT_LOADER' : return (
        <Box p={1}>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Skeleton animation="wave" variant="text" width="100%"/>
            <Box pb={10} />
        </Box>
        );

    case 'TEXT_LOADER2': return (
      <Box py={2}>
        <Skeleton animation="wave" variant="rect" width="100%" height={25}/>
      </Box>
    );

    case 'FORM_LOADER' : return(
      <Box p={2}>
        <Skeleton animation="wave" variant="text" height={40} width="15%" />
        <Box p={1} />
        <Paper>
          <Box py={4}>
            <Grid container direction="column" justifyContent="center" alignItems="center" >
              <Grid item sm={8} style={{width:"100%"}}>
                {SkeletonByCount({count: 6, props: {animation: "wave", variant:"text" ,width:"100%", height:40}})}
              </Grid>
            </Grid>
          </Box>
        </Paper>
        <Box pb={2}/>
        <Paper>
          <Box px={2} py={4}>
            {SkeletonByCount({count: 2, props: {animation: "wave", variant:"text" ,width:"100%", height:30}})}
          </Box>
        </Paper>
      </Box>
    )

    case 'FORM_LOADER2': return (
      <Box p={2}>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item sm={11}>
            <Skeleton animation="wave" variant="text" width="25%" height={40} />
          </Grid>
          {/* <Grid item sm={1}>
            <Skeleton animation="wave" variant="text" width="100%" height={40} />
          </Grid> */}
        </Grid>
        <Box pb={2}/>
        {SkeletonByCount({count: 5, props: {animation: "wave", variant:"text" ,width:"100%", height:30}})}
      </Box>
    );

    case 'THREE_SLIM_LOADER_WITH_WHITE_BG' : return (
        <Paper>
            <Box px={2} py={6}>
                <Skeleton animation="wave" variant="text" width="100%"/>
                <Skeleton animation="wave" variant="text" width="100%"/>
                <Skeleton animation="wave" variant="text" width="100%"/>
            </Box>
        </Paper>
        );
        
    case 'FULL_PAGE_LOADER' : return (
      <Box p={2}>
        <Skeleton animation="wave" variant="text" height={20} width="20%" />
        <Skeleton animation="wave" variant="text" height={60} width="40%" />
        <Box pt={2} />
        <Skeleton animation="wave" variant="text" height={20} width="20%" />
        <Skeleton animation="wave" variant="text" height={60} width="70%" />
        <Box pt={2} />
        <Skeleton animation="wave" variant="text" height={30} width="100%" />
        <Skeleton animation="wave" variant="text" height={30} width="100%" />
        <Skeleton animation="wave" variant="text" height={30} width="100%" />
        <Skeleton animation="wave" variant="text" height={30} width="100%" />
      </Box>
    )

    case 'FULL_PAGE_LOADER1' : return (
        <Box p={2}>
            <Skeleton animation="wave" variant="text" height={30} width="100%" />
            <Skeleton animation="wave" variant="text" height={30} width="95%" />
            <Skeleton animation="wave" variant="text" height={30} width="100%" />
            <Skeleton animation="wave" variant="text" height={30} width="90%" />
            <Skeleton animation="wave" variant="text" height={30} width="93%" />
            <Skeleton animation="wave" variant="text" height={30} width="100%" />
            <Skeleton animation="wave" variant="text" height={30} width="90%" />
            <Skeleton animation="wave" variant="text" height={30} width="100%" />
        </Box>
    );
    
    case 'FULL_PAGE_LOADER2' : return (
        <Paper>
            <Box p={2}>
                <Skeleton animation="wave" variant="text" height={30} width="100%" />
                <Skeleton animation="wave" variant="text" height={30} width="95%" />
                <Skeleton animation="wave" variant="text" height={30} width="100%" />
                <Skeleton animation="wave" variant="text" height={30} width="90%" />
                <Skeleton animation="wave" variant="text" height={30} width="93%" />
                <Skeleton animation="wave" variant="text" height={30} width="100%" />
                <Skeleton animation="wave" variant="text" height={30} width="90%" />
                <Skeleton animation="wave" variant="text" height={30} width="100%" />
            </Box>
        </Paper>
    );

    case 'FULL_PAGE_LOADER3' : return (
        <Box p={2}>
            <Skeleton animation="wave" variant="text" width="100%" height={50} />
            <Box pt={1} />
            <Skeleton animation="wave" variant="rect" width="100%" height={120} />
        </Box>
    );
    
    case 'FULL_PAGE_LOADER4' : return (
        <Box p={2}>
            <Skeleton animation="wave" variant="rect" width="100%" height={100} />
            <Box pt={4} />
            <Skeleton animation="wave" variant="rect" width="100%" height={150} />
        </Box>
    );

    case 'FULL_PAGE_LOADER5' : return (
        <Box p={2}>
            <Box pt={15} px={30}>
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Box pt={1} />
                <Skeleton animation="wave" variant="rect" width="100%" height={150} />
                <Box pt={4} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Box pt={1} />
                <Skeleton animation="wave" variant="rect" width="100%" height={50} />
                <Box pt={4} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Box pt={1} />
                <Skeleton animation="wave" variant="rect" width="100%" height={50} />
                <Box pt={4} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Box pt={1} />
                <Skeleton animation="wave" variant="rect" width="100%" height={100} />
            </Box>
        </Box>
    );

    case 'FULL_PAGE_LOADER6' : return (
        <Box p={2}>
            <Box pt={1} px={30}>
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Box pt={1} />
                <Skeleton animation="wave" variant="rect" width="100%" height={150} />
                <Box pt={4} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Box pt={1} />
                <Skeleton animation="wave" variant="rect" width="100%" height={150} />
                <Box pt={4} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Box pt={1} />
                <Skeleton animation="wave" variant="rect" width="100%" height={50} />
            </Box>
        </Box>
    );

    case 'FULL_PAGE_LOADER7' : return (
        <Box>
            <Box mt={5} />
            <Paper>
                <Box p={2}>
                    <Skeleton animation="wave" variant="text" width="100%" height={30} />
                    <Skeleton animation="wave" variant="text" width="100%" height={30} />
                    <Skeleton animation="wave" variant="text" width="100%" height={30} />
                    <Skeleton animation="wave" variant="text" width="100%" height={30} />
                </Box>
            </Paper>
        </Box>
    );

    case 'FULL_PAGE_LOADER8' : return (
        <Box p={2}>
            <Skeleton animation="wave" variant="rect" width="100%" height={150} />
            <Box pt={1} />
            <Skeleton animation="wave" variant="text" width="100%" height={60} />
        </Box>
    );

    case 'FULL_PAGE_LOADER9' : return (
        <Box>
            <Box p={2}>
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
                <Skeleton animation="wave" variant="text" width="100%" height={30} />
            </Box>
            <Box pb={10} />
        </Box>
    );

    case 'FULL_PAGE_LOADER10' : return (
        <Box p={2}>
            <Skeleton animation="wave" variant="text" width="30%" height={30} />
            <Box pt={1} />
            <Skeleton animation="wave" variant="rect" width="100%" height={50} />
            <Box pt={2} />
            <Skeleton animation="wave" variant="text" width="30%" height={30} />
            <Box pt={1} />
            <Skeleton animation="wave" variant="rect" width="100%" height={150} />
        </Box>
    );

    case 'FULL_PAGE_LOADER11' : return (
      <Box p={2}>
          <Skeleton animation="wave" variant="rect" width="100%" height={150} />
          <Box pt={4} />
          <Skeleton animation="wave" variant="rect" width="100%" height={80} />
          <Box pt={4} />
          <Skeleton animation="wave" variant="rect" width="100%" height={80} />
          <Box pt={4} />
          <Skeleton animation="wave" variant="rect" width="100%" height={80} />
      </Box>
    );

    case 'FULL_PAGE_LOADER12': return (
      <Box p={2}>
        {SkeletonByCount({count: 8, props: {animation: "wave", variant:"text", height:30}, width:["100%","95%","100%","90%","93%","100%","90%","100%"]})}
      </Box>
    );
    
    case 'SIDE_PANEL_MULTI_LINE_AREA': return (
        <Grid container spacing={3}>
           <Grid item sm={3}>
            <Skeleton variant="rect" animation="wave" height={200}/>
           </Grid>
           <Grid item sm={9}>
           <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" width="60%" animation="wave"/>
            <Skeleton variant="rect" animation="wave" height={158}/>
           </Grid>
        </Grid>
    );
    case 'MULTI_LINE_AREA': return (
        <Grid item>
            <Skeleton variant="text" width="60%" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" width="60%" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="rect" animation="wave" height={158}/>
        </Grid>
    );
    case 'TITLE_LINE': return (
        <Grid item>
            <Skeleton variant="text" width="30%" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
        </Grid>
    );

    case 'GRID_3': return (
      <Box p={1} display="flex" justifyContent="space-between">
        <Skeleton animation="wave" width="30%" height={50}/>
        <Skeleton animation="wave" width="30%" height={50}/>
        <Skeleton animation="wave" width="30%" height={50}/>
      </Box>
    )

    case 'UNIFIED_CHART_OWNER_POPOP' : return (<Skeleton variant="text" animation="wave" height="30px" style={{marginTop: "-10px"}}/>);

    case 'UNIFIED_PAGE_LOADER' : return (
        <Box p={1}>
           <Box p={1}>
              <Skeleton animation="wave" variant="text" width="30%" height={20} />
            </Box>
            <Box p={1}>
              <Divider />
            </Box>
            <Box p={1}>
              <Skeleton animation="wave" variant="text" width="60%" height={20} />
              <Box pt={1} />
              <Skeleton animation="wave" variant="text" width="100%" height={20} />
              <Box pt={1} />
              <Skeleton animation="wave" variant="text" width="100%" height={20} />
              <Box pt={1} />
              <Skeleton animation="wave" variant="text" width="100%" height={20} />
            </Box>
        </Box>
    );
    
    default: return (
        <Grid item>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
            <Skeleton variant="text" animation="wave"/>
        </Grid>
    )
  }
}

const LinearProgressWithLabel = ({boxProps, handleCancel, showCancelButton=false, ...rest}) => {
  return (
    <Fragment>
      <Box display="flex" alignItems="center" {...boxProps}>
        <Box width="100%" mr={1}>
          <LinearProgress variant="determinate" {...rest} />
        </Box>
        <Box minWidth={35}>
          <Typography variant="body2" color="textSecondary">{`${Math.round(
            rest.value,
            )}%`}</Typography>
        </Box>
        {showCancelButton && <Box><Button color="secondary" onClick={handleCancel}>Cancel</Button></Box>}
      </Box>
    </Fragment>
  );
}

const useCustomTxtStyles = makeStyles({ 
  root: { 
    fontWeight: 500,  
    fontSize: '14px'  
  } 
});

const BoldTxt = (props) => {  
  const {children, className} = props;  
  const classes = useCustomTxtStyles(); 
  const _className = clsx(className, classes.root); 
  return (  
    <Typography classes={{root: _className}} display="inline" {...props}> 
      { children }  
    </Typography> 
  ) 
}

@observer
class MoreLessInfiniteScroll extends React.Component {
  startIndex = 0;
  maxItems = 200;
  constructor(props) {
    super(props);
    this._vState = observable({
      data : props.data,
      items: props.data.slice(0, this.maxItems),
      hasMore: props.data.length > this.maxItems,
      keyName: props.keyName,
      className: 'nodisplay'
    });
  }
  componentDidUpdate(prevProps, prevState) {
    if(prevProps.data.length != this.props.data.length){
      this._vState.data = this.props.data;
      this._vState.items = this.props.data.slice(0, this.startIndex + this.maxItems);
      this._vState.hasMore = this._vState.data.length != this._vState.items.length;
    }
  }

  @action
  fetchMoreData = () => {
    this.startIndex += this.maxItems;
    setTimeout(() => {
      this._vState.items = this._vState.items.concat(this._vState.data.slice(this.startIndex, this.startIndex + this.maxItems));
      this._vState.hasMore = this._vState.data.length != this._vState.items.length;
    }, 100);
  };
  onMouseEnter = (e) => {
    this._vState.className = '';
  }
  onMouseLeave = (e) => {
    this._vState.className = 'nodisplay';
  }

  render() {
    const {items, hasMore, keyName, className} = this._vState;
    const {fetchMoreData, maxItems} = this
    const {modelId, renderItems, data, scrollableDivProps={}} = this.props;
    return (
        <div onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave} className={"position-relative"}>
          <div id={"scrollableDiv"+modelId} style={{ maxHeight: 156, overflow: "auto" }} {...scrollableDivProps}>
            <InfiniteScroll
                dataLength={items.length}
                next={fetchMoreData}
                hasMore={hasMore}
                loader={<div className={"infinite-scroll-loading"}>Loading...</div>}
                scrollableTarget={"scrollableDiv"+ modelId}
                className={"d-flex d-flex-wrap"}
            >
              {renderItems ? renderItems(items) : items.map((item, index) => (
                  <Chip key={index} className="wrap-tags" size="small" label={keyName ? item[keyName] : item} />
              ))}
            </InfiniteScroll>
          </div>
          <div className={className+" infinite-scroll-count"}>{`Showing ${items.length} out of ${data.length}`}</div>
        </div>
    );
  }
}

const ColumnDropListComponent = observer(({ allColumns, handleCheck, colButtonAttr, addGrid=true,
  showDefaultColums=true, menuItemProps={}, ...props
}) => {
  let addBlankGrid = !isUndefined(props.addBlankGrid) ? props.addBlankGrid : true;

  let popper = (
    <PopperMenu
      buttonType="IconButton"
      buttonProps={{className: 'pull-right', ...colButtonAttr}}
      title="Filter Columns"
      menuListProps={{ className: 'filterDrop' }}
      label={
        <Tooltip arrow placement="top" title="Show/Hide Columns">
          <ViewColumnIcon />
        </Tooltip>
      }
      renderCustomMenus={(handleClose) => {
        return allColumns && allColumns.map((column, i) => (
          <Observer>
            {
              () => {
                if (showDefaultColums || !column.isDefault) {
                  return (
                    <MenuItem dense={false} eventkey={i} onClick={() => handleCheck(i)} key={i} {...menuItemProps}>
                      <Checkbox checked={column.isSelected} className="checkbox-padding" size="small"/>
                      <span className="m-l-xs pull-right">{column.title}</span>
                    </MenuItem>
                  )
                }
                return null;
              }
            }
          </Observer>
        ))
      }}
      {...props}
    />
  )

  if (addGrid) {
    return (
      <Grid container spacing={1}>
        {addBlankGrid && <Grid item xs={10} sm={10} md={12}></Grid>}
        <Grid item xs={10} sm={10} md={12}>
          {popper}
        </Grid>
      </Grid>
    )
  }

  return popper;
});

const TopAlerts = observer(function TopAlerts({title, data, onClick, className, colAttr={sm: 6, md: 3}}) {
  const models = f.models(data);
  const feedActivityList = models.length > 0 ? makeAccessDeniedTagProgressData(models.slice()) : [];
  return (
      <Grid item {...colAttr} className={className}>
          <div className="ibox top-listing-box">
              <div className="ibox-title">
                  <Typography component="h5">{title}</Typography>
              </div>
              <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                  <div className="ibox-content">
                      {
                          f.models(data).length > 0
                          ? <FeedActivityList data={feedActivityList} onClick={onClick} showPopover={false}/>
                          : <div className="text-center no-data">No Data Available</div>
                      }
                  </div>
              </Loader>
          </div>
      </Grid>
  );
})

class ContentViewMore extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: false,
      text: "view more"
    };
  }

  showMore = (e) => {
    e.preventDefault();
    if (this.state.text === "view more") {
      this.setState({ text: "less", data: true });
    } else {
      this.setState({ text: "view more", data: false });
    }
  }

  getIntialTextFromContent = (content) => {
    const { showMaxText } = this.props;
    return {
      initial: content.substr(0, showMaxText),
      moreText: content.substr(showMaxText)
    };
  }

  getActionTag = () => {
    const { text } = this.state;
    const { linkClass } = this.props;
    return <a className={!!linkClass ? `pull-right ${linkClass}` : ""} href="#!" onClick={this.showMore}>{text}</a>;
  }

  render() {
    const { text, data } = this.state;
    const { content, contentViewProps } = this.props;
    const { initial, moreText } = this.getIntialTextFromContent(content);
    return (
      <Box {...contentViewProps}>
        {initial}
        {text === 'view more' && moreText.length > 0 ? '...' : null}
        {(data)
          ? moreText
          : null
        }
        {(moreText.length > 0)
          ? <div>{this.getActionTag()}</div>
          : null
        }
      </Box>
    );
  }
}

ContentViewMore.defaultProps = {
  showMaxText: 200,
  content: ''
};

ContentViewMore.propTypes = {
  showMaxText: PropTypes.number,
  content: PropTypes.string
};

export {
  Select2,
  Loader,
  PaginationComponent,
  TooltipOverlay,
  SingleTag,
  RemainingTags,
  WrapTags,
  FeedActivityList,
  DiagnosticIbox,
  TopAccess,
  FeedElement,
  ImportForm,
  MoreLessComponent,
  VTagsSection,
  VVerificationMessages,
  ResourceLookupSelect2,
  HiveResourceLookupSelect2,
  HBaseResourceLookupSelect2,
  CassandraResourceLookupSelect2,
  AWSDynamoDBLookupSelect2,
  JDBCSelect2,
  HdfsResourceLookupSelect2,
  AWSS3ResourceLookupSelect2,
  AzureAdlsResourceLookupSelect2,
  GCSResourceLookupSelect2,
  TourManager2,
  PopperMenu,
  TabPanel,
  CustomProgressBar,
  OnlyPagerComponent,
  CustomPopover,
  SkeletonByCount,
  PrivaceraLoader,
  getSkeleton,
  BoldTxt,
  LinearProgressWithLabel,
  MoreLessInfiniteScroll,
  TooltipOverlayInfo,
  ColumnDropListComponent,
  TopAlerts,
  ExportForm,
  ContentViewMore
}