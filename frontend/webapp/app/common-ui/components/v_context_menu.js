import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {forEach, debounce, isEmpty} from 'lodash';
import {observer} from 'mobx-react';
import {observable} from 'mobx';

// Material Imports
import InfoIcon from '@material-ui/icons/Info';

import {PopperMenu} from 'common-ui/components/generic_components'

@observer
class VContextMenu extends Component {

  @observable _vState = {
    //openContextMenu: false
  }

  state = {
    style: {
      display: "none",
      position: "absolute",
      'zIndex': "9999",
      left: "0px",
      top: "0px"
    }
  }

  componentDidUpdate() {
    this.bindEvent();
  }

  componentDidMount() {
    this.contextMenu = ReactDOM.findDOMNode(this.contextMenu)
    this.rel1 = document.createRange();
    this.rel1.selectNode(ReactDOM.findDOMNode(this.cal1));
    this.rel2 = document.createRange();
    this.rel2.selectNode(ReactDOM.findDOMNode(this.cal2));
  }

  bindEvent() {
    const { tabelrefs } = this.props;
    let table = ReactDOM.findDOMNode(tabelrefs);
    if (!tabelrefs && !table) {
      return;
    }
    let ctxMenuList = table.getElementsByClassName('ctxMenu');
    if (ctxMenuList.length && ctxMenuList[0].onmouseup) {
        return;
    }

    forEach(ctxMenuList, (ctxMenu) => {
        ctxMenu.onmouseup = (e) => {
          this.mouseUpEvent(e)
        }
        ctxMenu.onmousedown = (e) => {
          this.mouseDownEvent();
        }
    });
    table.onmousedown = (e) => {
      this.mouseDownEvent();
    }
  }

  mouseDownEvent = (e) => {
      let style = Object.assign({}, this.state.style);
      style.display = "none";
      this.setState({style: style});
  }

  mouseUpEvent = (e) => {
    var selection;
    e.stopPropagation();

    try {
      var range = window.getSelection().getRangeAt(0);
      var selectionContents = range.cloneContents();
      selection = selectionContents.textContent;

      debounce(this.selectionCallBack, 1);
      this.selectionCallBack(selection, range, e)
    } catch (e) {
      console.warn(e);
    }
  }

  selectionCallBack = (selection, range, e) => {
    this._vState.openContextMenu = false;
    if (this.selectionText != selection.toString()) {
      this.selectionText = selection.toString();
    } else {
      this._vState.openContextMenu = false;
      return;
    }
    this.selectedTextNode = e.currentTarget;

    let style = Object.assign({}, this.state.style);
    if (selection && selection.toString() && (!isEmpty(selection.toString().trim()))) {
        var r = range.getBoundingClientRect();
        var rb1 = this.rel1.getBoundingClientRect();
        var rb2 = this.rel2.getBoundingClientRect();
        style.top = ((r.bottom - rb2.top)*100/(rb1.top-rb2.top) - 55) + 'px'; //this will place ele above the selection
        style.left = (r.left - rb2.left)*100/(rb1.left-rb2.left) + 'px'; //this will align the right edges together

        style.display = 'block';
    } else {
      style.display = "none";
    }
    this.setState({style: style});
  }

  handleContextMenuSelection = ({dataid}) => {
    this._vState.openContextMenu = false;
    this.contextMenu.style.display = "none";

    let columnkey = this.selectedTextNode.getAttribute('data-columnkey');
    if(!columnkey && !this.selectionText) {
      return;
    }

    this.props.callback && this.props.callback(dataid, columnkey, this.selectionText);
  }

  render() {
      const {_vState, state, handleContextMenuSelection} = this;

      return (
        <div>
          <div ref={ref => this.contextMenu = ref}
            style={state.style}
          >
            <PopperMenu 
              buttonType="IconButton"
              label={<InfoIcon color="primary"  />}  
              buttonProps={{size: 'small'}}
              menuOptions={[
                { 
                  label: 'Include',
                  onClick: handleContextMenuSelection,
                  dataid: 'I'
                },
                {
                  label: 'Exclude',
                  onClick: handleContextMenuSelection,
                  dataid: 'E'
                }
              ]}
            />
          </div>
          <div ref={ref => this.cal1 = ref} id="cal1">&nbsp;</div>
          <div ref={ref => this.cal2 = ref} id="cal2">&nbsp;</div>
        </div>
      )
  }
}

export default VContextMenu;