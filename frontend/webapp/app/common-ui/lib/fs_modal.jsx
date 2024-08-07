import React, {Component, Fragment} from 'react';

import {withStyles} from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import MuiDialogTitle from '@material-ui/core/DialogTitle';
import MuiDialogContent from '@material-ui/core/DialogContent';
import MuiDialogActions from '@material-ui/core/DialogActions';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import Typography from '@material-ui/core/Typography';
import Grow from '@material-ui/core/Grow';
import Slide from "@material-ui/core/Slide";
import FullscreenIcon from '@material-ui/icons/Fullscreen';
import FullscreenExitIcon from '@material-ui/icons/FullscreenExit';

const Transition = React.forwardRef(function Transition(props, ref) {
  return (
    <Slide
      data-testid="custom-dialog"
      direction="down"
      ref={ref}
      className="custom-dialog"
      unmountOnExit
      in
      timeout={2000}
      {...props}
    />
  );
});

const styles = (theme) => ({
  root: {
    margin: 0,
    padding: theme.spacing(2),
  },
  closeButton: {
    position: 'absolute',
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
  expandButton: {
    position: 'absolute',
    right: theme.spacing(8),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
});

const DialogTitle = withStyles(styles)((props) => {
  const { children, classes, onClose, onExpand, showExpandButton, titleProps, expanded, ...other } = props;
  return (
    <MuiDialogTitle disableTypography className={classes.root} {...other}>
      <Typography variant="h6" style={{maxWidth: '90%'}} {...titleProps}>{children}</Typography>
      {showExpandButton ? (
        <IconButton aria-label="expand" className={classes.expandButton} onClick={onExpand}>
          {!expanded ? <FullscreenIcon /> : <FullscreenExitIcon />}
        </IconButton>
      ) : null}
      {onClose ? (
        <IconButton aria-label="close" className={classes.closeButton} onClick={onClose}>
          <CloseIcon />
        </IconButton>
      ) : null}
    </MuiDialogTitle>
  );
});

const DialogContent = withStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
}))(MuiDialogContent);

const DialogActions = withStyles((theme) => ({
  root: {
    margin: 0,
    padding: theme.spacing(1),
  },
}))(MuiDialogActions);

const _styles = theme => createStyles({ // change to this
  scrollPaper: {
    alignItems: 'baseline'
  }
});

const defaultState = {
   show: false,
   title: '',
   btnOkText: '',
   btnCancelText: '',
   // btnSaveAsText: '',
   showOkButton: true,
   showCloseButton: true,
   showExpandButton: false,
   btnOkDisabled: false,
   children: null,
   showDivider: true,
   btnCancelColor: 'primary'
   // showSaveAs: false
}

class FSModal extends Component {
  constructor(props) {
    super(props);
    this.state = {...defaultState, isFullScreen: props.fullScreen};

  }
  show(state){
    var state = {...defaultState, ...(state || {})};
    state.show = true;
    if (state.btnOkDisabled == null) {
      state.btnOkDisabled = false;
    }
    this.setState(state);
  }
  sure = e => {
    e.stopPropagation();
    let resolve = this.props.dataResolve;
    if(resolve){
      resolve(e);
    }
  }
  cancel = (e) => {
    e.stopPropagation();
    let {reject} = this.props;
    if (reject) {
      reject()
    } else {
      this.hide()
    }
  }
  expand = () => {
    this.setState({isFullScreen: !this.state.isFullScreen})
  }
  
  hide = () => {
    this.setState({ show: false});
  }
  showOkButton(showOkButton=this.state.showOkButton) {
    this.setState({
      showOkButton
    })
  }
  okBtnDisabled(status) {
    this.setState({btnOkDisabled: status})
  }
  showHideOkButton(status) {
    this.setState({showOkButton: status})
  }
  showHideCloseButton(status) {
    this.setState({showCloseButton: status})
  }
  setOkButtonTxt(txt) {
    this.setState({btnOkText: txt});
  }
  updateState = (state={}) => {
    this.setState(state);
  }
  header(){
    const {opts, bodyProps, showExpandButton} = this.props;
    if (opts && opts.header &&  !opts.header.self) {
      return null;
    }
    let titleProps = {};
    if (opts && opts.header && opts.header.titleProps) {
      titleProps = opts.header.titleProps;
    }
    return (
      <DialogTitle id="customized-dialog-title" data-testid="customized-dialog-title" titleProps={titleProps} showExpandButton={showExpandButton} onExpand={this.expand} onClose={this.cancel} expanded={this.state.isFullScreen}>
        {this.props["dataTitle"] || this.state.title}
      </DialogTitle>
    );
  }
  body(){
    const {opts, bodyProps} = this.props;
    const noModalClass = opts.footer.self ? '' : 'no-modal-footer';
    let children = this.props.children;
    if (typeof this.props.children == 'function') {
      children = this.props.children();
    }

    if (opts && opts.body && !opts.body.self) {
      return children;
    }

    return (<DialogContent dividers={this.state.showDivider} className={noModalClass} {...bodyProps} data-testid="modal-body">{children}</DialogContent>);
  }
  footer(){
    const { showCloseButton, btnCancelColor } = this.state;
    return (
      <DialogActions role="footer">
        {this.props.customFooterButtons && this.props.buttonComponent(this.state.btnOkDisabled)}
        { showCloseButton && 
          <Button data-test="modal-cancel-btn" color={btnCancelColor} className='modal-close--btn' onClick={this.cancel}>
            {this.state.btnCancelText || 'Close'}
          </Button>
        }
        { this.state.showOkButton && 
          <Button data-test="modal-ok-btn" variant="contained" color='primary' className='modal-save--btn' onClick={this.sure} disabled={this.state.btnOkDisabled}>
            {this.state.btnOkText || 'Save'}
          </Button>
        }
      </DialogActions>
    );
  }
  render() {
    const {opts, dataTitle, dataResolve, reject, animation=Grow, customFooterButtons, buttonComponent,
      scrollable = false, fullWidth=true, onEnter, bodyProps, showOkButton, showCloseButton, showExpandButton, fullScreen, ...rest} = this.props;
    if (!rest.maxWidth) {
      rest.maxWidth = 'sm';
    }
    return (
      <Fragment>
        <Dialog aria-labelledby="customized-dialog-title"
          data-testid="modal"
          open={this.state.show}
          onClose={this.cancel}
          onEnter={ onEnter && onEnter()}
          disableBackdropClick={true}
          disableEscapeKeyDown={true}
          fullWidth={fullWidth}
          TransitionComponent={Transition}
          TransitionProps={{tabIndex: ""}} /* Empty tabIndex to resolve the mozilla browser issue for date picker (hours/minutes) selection.*/
          scroll={scrollable ? 'body' : 'paper'}
          fullScreen={this.state.isFullScreen}
          {...rest}
        >
          {this.header()}
          {this.body()}
          {opts.footer.self ? this.footer() : null}
        </Dialog>
      </Fragment>
    );
  }
}

FSModal.defaultProps = {
  opts: {
    header: {
      self: true,
      titleProps: {}
    },
    body: {
      self: true
    },
    footer: {
      self: true
    }
  },
  bodyProps: {}
}

var _resolve;
var _reject;

class Confirm extends FSModal {
  show(state){
    var state = { ...defaultState, ...(state || {}) };
    state.show = true;
    if (!state.hasOwnProperty('showOkButton')) {
      state.showOkButton = defaultState.showOkButton;
    }
    if (!state.hasOwnProperty('btnOkText')) {
      state.btnOkText = defaultState.btnOkText;
    }
    if (!state.hasOwnProperty('btnCancelText')) {
      state.btnCancelText = defaultState.btnCancelText;
    }
    if (!state.hasOwnProperty('btnOkDisabled')) {
      state.btnOkDisabled = false;
    }
    if (!state.hasOwnProperty('showCloseButton')) {
      state.showCloseButton = true;
    }

    this.setState(state);
    let promise = new Promise(function(resolve, reject) {
      _resolve = resolve;
      _reject = reject;
    })
    return promise;
  }
  confirmDelete = (options) => {
    let deleteProps = {
      title: `Confirm Delete`,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text',
      ...options
    }
    return this.show(deleteProps)
  }
  sure = (e) => {
    e.stopPropagation();
    this.okBtnDisabled(true);
    _resolve(this);
  }
  cancel = (e) => {
    e.stopPropagation();
    _reject(this);
    this.hide();
  }
  header(){
    return (
      <DialogTitle id="customized-dialog-title" onClose={this.cancel} data-testid="confirm-dialog-title">
        {this.state.title}
      </DialogTitle>
    );
  }
  body(){
    if (this.props.children) {
      const {opts} = this.props;
      const noModalClass = opts.footer.self ? '' : 'no-modal-footer';
      return (
        <DialogContent data-testid="dialog-content" dividers={this.state.showDivider} className={`${noModalClass} w-b-bw`}>
          <Typography component="div" variant="body1" color="textSecondary">{this.props.children}</Typography>
        </DialogContent>
      );
    }

    if (this.state.children) {
      return (
        <DialogContent data-testid="dialog-content">
          <Typography component="div" variant="body1" color="textSecondary" className="w-b-bw">{this.state.children}</Typography>
        </DialogContent>
      );
    }
    return '';
  }
  footer(){
    const {btnCancelText, btnOkText, showOkButton, btnOkDisabled, btnOkVariant = "text", btnOkColor = "primary", btnCancelColor = "primary", showCloseButton} = this.state;
    return (
      <DialogActions role="footer">
        {
          showCloseButton && 
          <Button data-test="confirm-no-btn" color={btnCancelColor} onClick={this.cancel}>
          {btnCancelText || 'No'}
        </Button>
        }
        {
          showOkButton && 
          <Button data-test="confirm-yes-btn" variant={btnOkVariant} color={btnOkColor} onClick={this.sure} disabled={btnOkDisabled}>
            {btnOkText || 'Yes'}
          </Button>
        }
      </DialogActions>
    );
  }
}

export default FSModal;
export {Confirm};