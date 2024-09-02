import React, { Component, Fragment } from 'react';
import { withRouter } from 'react-router';
import { observer } from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import Tooltip from '@material-ui/core/Tooltip';
import Button from '@material-ui/core/Button';
import ClickAwayListener from '@material-ui/core/ClickAwayListener';
import IconButton from '@material-ui/core/IconButton';
import Paper from '@material-ui/core/Paper';
import Popover from '@material-ui/core/Popper';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Box from '@material-ui/core/Box';
import Badge from "@material-ui/core/Badge";

/** material ui icon imports **/
import FileCopyIcon from '@material-ui/icons/FileCopy';
import VisibilityIcon from '@material-ui/icons/Visibility';
import PlaylistAddCheckIcon from '@material-ui/icons/PlaylistAddCheck';
import AddIcon from '@material-ui/icons/Add';
import EditIcon from '@material-ui/icons/Edit';
import CancelIcon from '@material-ui/icons/Cancel';
import GetAppRoundedIcon from '@material-ui/icons/GetAppRounded';
import PublishRoundedIcon from '@material-ui/icons/PublishRounded';
import DeleteIcon from '@material-ui/icons/Delete';
import RefreshIcon from '@material-ui/icons/Refresh';
import AssignmentTurnedInIcon from '@material-ui/icons/AssignmentTurnedIn';
import ArrowBackIosRoundedIcon from '@material-ui/icons/ArrowBackIosRounded';
import Alert from '@material-ui/lab/Alert';
import DoneIcon from '@material-ui/icons/Done';
import BlockIcon from '@material-ui/icons/Block';
import HighlightOffIcon from '@material-ui/icons/HighlightOff';
import FilterListIcon from "@material-ui/icons/FilterList";

import { Utils } from 'common-ui/utils/utils';
import { ImportForm } from 'common-ui/components/generic_components';
import FSModal from 'common-ui/lib/fs_modal';
import { Checkbox } from 'common-ui/components/filters';

const AddButton = ({ colAttr, label, iconClass, /*icon,*/ addCol, ...props }) => {
    let button = (
        <Button {...props}>
            {label}
        </Button>
    )
    if (addCol) {
        return (
            <Grid item {...colAttr}>
                {button}
            </Grid>
        )
    }
    return button;
}
AddButton.defaultProps = {
    label: 'Add',
    variant: 'contained',
    color: 'primary',
    size: 'medium',
    className: 'pull-right responsive-add',
    'data-test': 'add-btn',
    'aria-label':'Add button',
    colAttr: {
        xs: 2
    },
    addCol: true,
    // icon: <AddIcon fontSize="small" />
}

const AddButtonWithPermission = ({ permission, ...props }) => {
    if (permission && permission.update) {
        return <AddButton {...props} />;
    }
    return null;
}

const AddInLineButtonWithPermission = ({ permission, tooltipLabel, fontSize="small", ...props }) => {
    if (permission && permission.update) {
        return (
            <Tooltip arrow placement="top" title={tooltipLabel}>
                <IconButton {...props} aria-label={tooltipLabel}>
                    <AddIcon fontSize={fontSize} />
                </IconButton>
            </Tooltip>
        )
    }
    return null;
}

const CustomAnchorBtn = ({
    tooltipLabel = '', icon, tooltipProps={}, showToolTipOnDisabled=false, ...props
}) => {
    let button = (
        <IconButton size="small" data-test={tooltipLabel} aria-label={tooltipLabel} {...props}>
            {icon}
        </IconButton>
    )
    if (props.disabled && !showToolTipOnDisabled) {
        return button;
    }
    return (
        <Tooltip arrow placement="top" title={tooltipLabel} {...tooltipProps}>
            {button}
        </Tooltip>
    )
}

const PreviewAnchorBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title={'Preview'}>
            <IconButton size="small" data-test="view" data-track-id="preview" {...props} aria-label={'Preview'}>
                <VisibilityIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}
const CloneAnchorBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title="Clone">
            <IconButton size="small" data-test="view" data-track-id="copy" aria-label="Clone" {...props}>
                <FileCopyIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}

const EditAnchorBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title="Edit">
            <IconButton size="small" data-test="edit" data-track-id="edit" aria-label="Edit" {...props}>
                <EditIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}

const TestRegexBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title="Test Expression">
            <IconButton size="small" data-test="regex" data-track-id="regex" aria-label="Test Expression" {...props}>
                <AssignmentTurnedInIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}

const DeleteAnchorBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title="Delete">
            <IconButton size="small" data-test="delete" data-track-id="delete" aria-label="delete" {...props}>
                <DeleteIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}

const VerifyAnchorBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title="Verify">
            <IconButton size="small" data-test="verify" data-track-id="verify" aria-label="verify" {...props}>
                <PlaylistAddCheckIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}

const RejectRequestBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title="Reject">
            <IconButton size="small" data-test="Reject" data-track-id="reject" aria-label="Reject" {...props}>
                <BlockIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}

const AcceptRequestBtn = ({ ...props }) => {
    return (
        <Tooltip arrow placement="top" title="Accept">
            <IconButton size="small" data-test="Accept" data-track-id="accept" aria-label="Accept" {...props}>
                <DoneIcon color="primary" fontSize="inherit" />
            </IconButton>
        </Tooltip>
    )
}

const ReadRequestBtn = ({ ...props }) => {
  return (
    <Tooltip arrow placement="top" title="Read"> 
      <IconButton size="small" data-test="Read" aria-label="Read" data-track-id="read" {...props}>
        <HighlightOffIcon color="primary" fontSize="inherit" />
      </IconButton>
    </Tooltip>
  );
};

const ActionButtons = ({
    onEditClick, onDeleteClick, onPreviewClick, onRegexClick, showPreview, showRegexBtn, hideEdit,
    hideDelete, rejectRequest, onRejectRequest, onAcceptRequest, acceptRequest, readRequest,
    onReadRequest, showClone, onCloneClick, ...props 
}) => {
    return (
        <Fragment>
            {showRegexBtn && <TestRegexBtn onClick={onRegexClick} />}
            {showPreview && <PreviewAnchorBtn onClick={onPreviewClick} />}
            {!hideEdit && <EditAnchorBtn onClick={onEditClick} />}
            {!hideEdit && showClone && <CloneAnchorBtn onClick={onCloneClick} />}
            {!hideDelete && <DeleteAnchorBtn onClick={onDeleteClick} />}
            {!!rejectRequest && <RejectRequestBtn {...props.rejectRequestBtnProps} onClick={onRejectRequest}/>}
            {!!acceptRequest && <AcceptRequestBtn {...props.acceptRequestBtnProps} onClick={onAcceptRequest}/>}
            {readRequest && <ReadRequestBtn {...props.readRequestBtnProps} onClick={onReadRequest}/>}
        </Fragment>
    )
}


const ActionButtonsWithPermission = ({ permission = {}, ...props }) => {
    return (
        <ActionButtons
            hideEdit={!permission.update}
            hideDelete={!permission.delete}
            {...props}
        />
    )
}

const ExportButton = ({label="", type, icon=<PublishRoundedIcon />, iconClass="", iconSize="small", title, ...btnProps}) => {
    if (type && type === 'label') {
        return (
            <Button {...btnProps}>
                {icon}
                {label}
            </Button>
        );
    } else {
        return (
            <Tooltip arrow placement="top" title={label} aria-label={label}>
                <IconButton {...btnProps}>
                    <PublishRoundedIcon fontSize={iconSize} />
                </IconButton>
            </Tooltip>
        );
    }
}
ExportButton.defaultProps = {
    // variant: "contained",
    color: 'primary'
}

class ImportButton extends Component{
    render() {
        const { label = "", type, iconClass = "", iconSize = "small", title, ...btnProps } = this.props;
        if (type && type === 'label') {
            return (
                <Button {...btnProps}>
                    <GetAppRoundedIcon /> {label}
                </Button>
            );
        } else {
            return (
                <Tooltip arrow placement="top" title={label || 'Import'} aria-label={label || 'Import'}>
                    <IconButton {...btnProps}>
                        <GetAppRoundedIcon />
                    </IconButton>
                </Tooltip>
            );
        }
    }
}

ImportButton.defaultProps = {
    // variant: "contained",
    color: 'primary'
}

const CancelButton = ({ label = "", iconClass = "", ...btnProps }) => {
    return (
        <Tooltip arrow placement="top" title="Cancel" aria-label="Cancel">
            <IconButton {...btnProps}>
                <CancelIcon fontSize="small" /> {label}
            </IconButton>
        </Tooltip>
    );
}
CancelButton.defaultProps = {
    variant: "contained",
    // color: 'secondary'
}

const RefreshButton = ({ wrapRow, wrapItem, className, onClick, colAttr, iconProps, pullRight, pullLeft, ...props }) => {
    let pullClass = '';
    if (pullRight) {
        pullClass = "pull-right";
    }
    if (pullLeft) {
        pullClass = "pull-left";
    }
    let button = (
        <Tooltip arrow placement="top" title="Refresh" aria-label="Refresh page">
            <IconButton className={`${pullClass} ${className}`} onClick={onClick} {...props} >
                <RefreshIcon fontSize="inherit" {...iconProps} />
            </IconButton>
        </Tooltip>
    )
    if (wrapItem) {
        return <Grid item {...colAttr}>{button}</Grid>
    }
    return button;
}
RefreshButton.defaultProps = {
    className: "",
    wrapItem: true,
    colAttr: { sm: 4, md: 1 },
    iconProps: {},
    pullRight: true,
    pullLeft: false,
    onClick: null,
    'data-testid': 'refresh-btn'
}

const FilterButton = ({ wrapItem, className, onClick, colAttr, iconProps, wrapBadge, wrapBadgeCount, ...props }) => {

    let filterListIcon = <FilterListIcon color="primary" fontSize="inherit" {...iconProps} />;
    let button = (
        <Tooltip arrow placement="top" title="Filter">
            <IconButton className={`date-widget ${className}`} onClick={onClick} {...props}>
                {wrapBadge ?
                    <Badge
                        badgeContent={wrapBadgeCount || undefined}
                        showZero
                        color="primary"
                        aria-hidden="true"
                    >
                        {filterListIcon}
                    </Badge>
                    : filterListIcon
                }
            </IconButton>
        </Tooltip>
    )
    if (wrapItem) {
        return <Grid item {...colAttr}>{button}</Grid>
    }
    return button;
}
FilterButton.defaultProps = {
    className: "",
    wrapItem: true,
    colAttr: { sm: 4, md: 1 },
    iconProps: {},
    onClick: null,
    wrapBadge: false,
    wrapBadgeCount: undefined
}

const BackButton = withRouter(({
    showIcon = true, history, location, staticContext, match, containerProps = {}, children=null, ...props
}) => {
    let icon = <ArrowBackIosRoundedIcon color="action" />;
    /*if (showIcon) {
        icon = <ArrowBackIosRoundedIcon color="action" />
    }*/
    return (
        <Box display="flex" alignItems="center" {...containerProps}>
            <Tooltip arrow placement="top" title="Back">
                <IconButton size="small" aria-label="Back" data-test={"back-btn"} onClick={() => history.goBack()} {...props} >
                    {icon}
                </IconButton>
            </Tooltip>
            {children}
        </Box>
    )
})
BackButton.defaultProps = {
    color: 'default',
    containerProps: {}
}

const CanRead = ({ permission = {}, children }) => {
    if (permission.read) {
        return children;
    }
    return null;
}

const CanUpdate = ({ permission = {}, children }) => {
    if (permission.update) {
        return children;
    }
    return null;
}

const CanDelete = ({ permission = {}, children }) => {
    if (permission.delete) {
        return children;
    }
    return null;
}

const CanExport = ({ permission = {}, children }) => {
    if (permission.export) {
        return children;
    }
    return null;
}

const CanReadOrUpdate = ({ permission = {}, children }) => {
    if (permission.read || permission.update) {
        return children;
    }
    return null;
}

const CanUpdateOrDelete = ({ permission = {}, children }) => {
    if (permission.update || permission.delete) {
        return children;
    }
    return null;
}

@observer
class ImportExportsOptions extends Component {
    state = {
        extraImportOptions: {},
        openPopper: false
    }
    constructor(props) {
        super(props);
        this.importRef = React.createRef();
        this.importFileRef = React.createRef();
    }
    enableExport = () => {
        if (!this.props.exportAll) {
            this.props.importExportUtil.enableExport()
        } else {
            this.handleCancel();
        }
        this.props.onExportClick && this.props.onExportClick();
    }
    handlePopperToggle = () => {
        this.setState({ openPopper: !this.state.openPopper });
    }
    handleCancel = () => {
        this.props.importExportUtil.resetExport();
        this.props.onExportCancel && this.props.onExportCancel();
    }
    handleImport = () => {
        this.props.importExportUtil.enableImport();
        this.setState({ extraImportOptions: {} }, () => {
            this.importRef.show({
                btnOkText: "Import"
            });
        })
    }
    handleImportResolve = () => {
        if (this.importFileRef && this.importFileRef.getFormData && this.importFileRef.checkIfFileAddedOrNot()) {

            const data = this.importFileRef.getFormData();

            if (this.props.extraImportOptions) {
                const { extraImportOptions } = this.state;

                Object.keys(extraImportOptions).forEach(opt => {
                    data.append(opt, extraImportOptions[opt]);
                })
            }
            this.props.onImport && this.props.onImport(data, this.importRef);
        }
    }
    handleExtraOptionClick = key => e => {
        const { extraImportOptions } = this.state;
        if (extraImportOptions[key]) {
            extraImportOptions[key] = false;
        } else {
            extraImportOptions[key] = true;
        }
        this.setState({ extraImportOptions });
    }
    createExtraImportOptions = opts => {
        const { extraImportOptions } = this.state;

        return Object.keys(opts).map(opt => {
            const HTML = [];
            if (opt == "checkbox") {
                opts[opt].forEach((check, i) => {
                    HTML.push(
                        <Checkbox
                            key={`check_${1}`}
                            checked={extraImportOptions[check.value]}
                            onClick={this.handleExtraOptionClick(check.value)}
                            labelText={check.label}
                        />
                    )
                    if (extraImportOptions[check.value]) {
                        HTML.push(
                            <Alert severity="warning" key={`clean_${1}`}>
                                Clean Previous will remove all the existing rules
                            </Alert>
                        );
                    }
                })
            }
            return HTML;
        })
    }
    render() {
        let { importExportUtil, exportType, callbacks, totalCheckboxCount, permission,
            handleSelect, onExportClick, onImport, handleExport,
            onExportCancel, extraImportOptions, exportAll, ...otherProps } = this.props;

        if (totalCheckboxCount == null && importExportUtil) {
            totalCheckboxCount = importExportUtil.selectedCount;
        }

        return (
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    {
                        !importExportUtil.isExport &&
                        <CanUpdate permission={this.props.permission}>
                            <ImportButton {...otherProps} className="m-r-sm" label={'Import'} aria-label={'Import'} type='label' onClick={this.handleImport} />
                        </CanUpdate>
                    }
                    {
                        exportType == undefined ?
                            (importExportUtil.isExport
                                ?
                                <Fragment>
                                    <ExportButton  {...otherProps} label={`Export (${importExportUtil.selectedCount})`}
                                        type='label'
                                        disabled={!importExportUtil.selectedCount}
                                        onClick={this.props.handleExport}
                                        size="small"
                                    />
                                    <CancelButton className="m-l-md" size={this.props.size || 'small'} onClick={this.handleCancel} />
                                </Fragment>
                                :
                                <CanExport permission={this.props.permission}>
                                    <ExportButton size="small" {...otherProps} label="Export"  aria-label="Export" type='label' onClick={this.enableExport} />
                                </CanExport>
                            )
                            :
                            (importExportUtil.isExport
                                ?
                                <Fragment>
                                    <ExportButton  {...otherProps} aria-label={`Export (${totalCheckboxCount})`} label={`Export (${totalCheckboxCount})`}
                                        type='label'
                                        disabled={!totalCheckboxCount}
                                        onClick={this.props.handleExport}
                                        size="small"
                                    />
                                    <CancelButton className="m-l-md" size={this.props.size || 'small'} onClick={this.handleCancel} />
                                </Fragment>
                                :
                                <CanExport permission={this.props.permission}>
                                    <ExportButtonWithDropdown
                                        {...this.props}
                                        label={this.props.label || "Export CSV"}
                                        aria-label={this.props.label || "Export CSV"}
                                        type='label'
                                        openPopper={this.state.openPopper}
                                        handlePopperToggle={this.handlePopperToggle}
                                        options={exportType}
                                        handleSelect={this.props.handleSelect}
                                        enableExport={this.enableExport}
                                        size="small"
                                    />
                                </CanExport>
                            )
                    }
                </Grid>
                <FSModal ref={ref => this.importRef = ref} dataTitle={"Import"} dataResolve={this.handleImportResolve}>
                    <ImportForm ref={ref => this.importFileRef = ref} {...this.props} />
                    {
                        extraImportOptions && this.createExtraImportOptions(extraImportOptions)
                    }
                </FSModal>
            </Grid>
        );
    }
}

class InLineImportExportOption extends ImportExportsOptions {
    render() {
        const { importExportUtil, className, importLabel = 'Import', exportLabel = 'Export', type, showDropdown = false, handleSelect, menuOptions = [], exportType, totalCheckboxCount, ...props } = this.props;
        let customProps = Utils.handleDeprecatedProps(props);
        const excludeProps = ['onExportClick', 'onImport', 'handleExport', 'onExportCancel', 'showprogress'];
        customProps = Utils.excludeProps(customProps, excludeProps);

        return (
            <Fragment>
                {
                    !importExportUtil.isExport &&
                    <CanUpdate permission={this.props.permission}>
                        <Tooltip arrow placement='top' title='Import'>
                            <ImportButton label={importLabel} type={type || 'icon'} onClick={this.handleImport} {...customProps} />
                        </Tooltip>
                    </CanUpdate>
                }
                {
                    importExportUtil.isExport || exportType
                        ?
                        <Fragment>
                            <ExportButton label={`${exportLabel} (${totalCheckboxCount})`} aria-label={`${exportLabel} (${totalCheckboxCount})`}
                                type={type || 'label'}
                                disabled={!totalCheckboxCount}
                                onClick={this.props.handleExport}
                                {...customProps}
                            />
                            <CancelButton className="m-l-sm" onClick={this.handleCancel} {...customProps} />
                        </Fragment>
                        : (
                            showDropdown
                                ?
                                <Tooltip arrow placement="top" title='Export'>
                                    <ExportButtonWithDropdown
                                        type={type || 'icon'}
                                        label={exportLabel}
                                        aria-label={exportLabel}
                                        openPopper={this.state.openPopper}
                                        handlePopperToggle={this.handlePopperToggle}
                                        handleSelect={handleSelect}
                                        options={menuOptions}
                                        enableExport={this.enableExport}
                                        {...customProps}
                                    />
                                </Tooltip>
                                : <CanExport permission={this.props.permission}>
                                    <ExportButton label={exportLabel} aria-label={exportLabel} type={type || 'label'} onClick={this.enableExport} {...customProps} />
                                </CanExport>
                        )
                }
                <FSModal ref={ref => this.importRef = ref} dataTitle={"Import"} dataResolve={this.handleImportResolve}>
                    <ImportForm ref={ref => this.importFileRef = ref} {...this.props} />
                    {
                        this.props.extraImportOptions && this.createExtraImportOptions(this.props.extraImportOptions)
                    }
                </FSModal>
            </Fragment>
        );
    }
}

class ExportButtonWithDropdown extends Component {
    constructor(props) {
        super(props);
        this.anchorRef = React.createRef();
        this.state = {
            openPopperSelf : false
        }
    }

    handlePopperToggleSelf = () => {
        this.setState({ openPopperSelf: !this.state.openPopperSelf });
    }

    handlePopperToggle = () => {
        const {handlePopperToggle} = this.props;
        if (handlePopperToggle) {
            handlePopperToggle()
        } else {
            this.handlePopperToggleSelf()
        }
    }       

    render() {
        const { label = "", type, openPopper, iconClass = '', handleSelect, options, callbacks, permission, enableExport, menukey = "label", menuvalue = 'value',
            bsStyle, size = 'small', className = "inline-flex", ...btnProps} = this.props;
        let customProps = Utils.handleDeprecatedProps({ bsStyle, size, className, ...btnProps });
        const excludeProps = ['handlePopperToggle', 'totalCheckboxCount', 'onExportClick', 'onImport', 'handleExport', 'onExportCancel', 'importExportUtil', 'exportType', 'showprogress']
        customProps = Utils.excludeProps(customProps, excludeProps);
        return (
            <Fragment>
                {type && type === 'label' ?
                    <Button
                        ref={this.anchorRef}
                        key={0}
                        onClick={this.handlePopperToggle}
                        color="primary"
                        {...customProps}
                    >
                        <PublishRoundedIcon /> {label}
                    </Button>
                    :
                    <Tooltip arrow placement="top" title={"Export"}>
                        <IconButton
                            ref={this.anchorRef}
                            key={0}
                            onClick={this.handlePopperToggle}
                        >
                            <PublishRoundedIcon />
                        </IconButton>
                    </Tooltip>
                }

                <Popover
                    open={openPopper || this.state.openPopperSelf}
                    anchorEl={this.anchorRef.current}
                    onClose={this.handlePopperToggle}
                    style={{zIndex: 999}}
                >
                    <Paper>
                        <ClickAwayListener onClickAway={this.handlePopperToggle}>
                            <MenuList autoFocusItem={openPopper || this.state.openPopperSelf}>
                                {options.map((opt, i) => (
                                    <MenuItem key={i} onClick={() => {
                                        handleSelect(opt[menuvalue]);
                                        enableExport();
                                        this.handlePopperToggle();
                                    }}>
                                        {opt[menukey]}
                                    </MenuItem>
                                ))}
                            </MenuList>
                        </ClickAwayListener>
                    </Paper>
                </Popover>
            </Fragment>
        )
    }
} 


class CommandDisplay extends Component {
    state = {
        copyState: false
    }
    oPos = {};
    timeout = null;

    handleMouseOut() {
        clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            this.setState({ copyState: false });
        }, 200);
    }

    copyHiddenContent = content => {
        const div = document.createElement("div");

        div.setAttribute('id', 'copy-content')
        div.setAttribute('data-clipboard-text', content)
        div.style = "position: absolute; left: -1000px; top: -1000px";

        document.body.appendChild(div);
        Utils.copyToClipboardV2('copy-content')

        document.body.removeChild(div);
    }

    componentWillUnmount() {
        this.timeout && clearTimeout(this.timeout);
    }
    handleClick = (e) => {
        e?.stopPropagation();
        if (this.props.hideContent) {
            this.copyHiddenContent(this.props.command)
        } else {
            Utils.copyToClipboardV2(this.props.id);
        }
        this.setState({ copyState: true });
    }
    render() {
        const { tooltipWrapperClass, showCommand, commandDisplayProps, anchorClass, hideContent, children, childrenAsTarget, tootipProps, contentProps } = this.props;
        return (
            <div key={this.props.command} {...commandDisplayProps}>
                {!childrenAsTarget && children}
                {!hideContent && <div id={this.props.id} className='w-b-bw' data-clipboard-text={this.props.command} {...contentProps}>{showCommand ? this.props.command : null}</div>}
                <div id="tooltip-target" className={tooltipWrapperClass} onMouseOut={() => this.handleMouseOut()}>
                    <Tooltip arrow id={`tooltip-top`} placement="top" className="copy-tooltip"
                        title={this.state.copyState ? "Copied!" : "Copy to Clipboard"}
                        {...tootipProps}
                    >
                        {
                            childrenAsTarget ?
                                <span onClick={this.handleClick}>
                                    {children}
                                </span>
                            :
                                <IconButton className={anchorClass} onClick={this.handleClick}>
                                    <FileCopyIcon fontSize="small" color="primary" />
                                </IconButton>
                        }
                    </Tooltip>
                </div>
            </div>
        )
    }
}
CommandDisplay.defaultProps = {
    commandDisplayProps: {
        className: 'command-display d-flex align-items-center justify-content-between'
    },
    showCommand: true,
    handleMouseOut: true,
    anchorClass: '',
    hideContent: false,
    childrenAsTarget: false,
    tootipProps: {},
    tooltipWrapperClass: "",
    contentProps: {}
}

class CopyClipboardInliner extends CommandDisplay {
    render() {
        const { commandDisplayProps, anchorClass, children, command, icon, 
            copiedTxt="Copied!", copiedToTxt="Copy to Clipboard" } = this.props;

        return (
            <span key={command} {...commandDisplayProps}>
                <span className="text-right m-r-xs" id="tooltip-target" onMouseOut={() => this.handleMouseOut()}>
                    <CustomAnchorBtn
                        tooltipLabel={this.state.copyState ? copiedTxt : copiedToTxt}
                        size="small"
                        className={anchorClass}
                        icon={icon || <FileCopyIcon color="primary" fontSize="inherit" />}
                        onClick={(e) => {
                            this.copyHiddenContent(command);
                            this.handleClick && this.handleClick(e);
                        }}
                    />
                </span>
                {children && <span className="resourceName">{children}</span>}
            </span>
        )
    }
}

export {
    AddButton,
    AddButtonWithPermission,
    CustomAnchorBtn,
    EditAnchorBtn,
    DeleteAnchorBtn,
    ActionButtons,
    ActionButtonsWithPermission,
    RefreshButton,
    BackButton,
    ExportButton,
    CancelButton,
    CanRead,
    CanUpdate,
    CanDelete,
    CanExport,
    CanReadOrUpdate,
    CanUpdateOrDelete,
    ImportExportsOptions,
    CommandDisplay,
    VerifyAnchorBtn,
    InLineImportExportOption,
    AddInLineButtonWithPermission,
    ExportButtonWithDropdown,
    CopyClipboardInliner,
    FilterButton,
    ImportButton
}
