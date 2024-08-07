import React, { Component } from 'react';

import TableRow from '@material-ui/core/TableRow';

export default class DraggableTr extends Component {
  state = {}

  onMouseDown = (e) => {
    const target = this.getTrNode(e.target);
    if (target) {
      target.setAttribute('draggable', true);
      target.ondragstart = this.onDragStart;
      target.ondragend = this.onDragEnd;
    }
  }

  onDragStart = (e) => {
    const target = this.getTrNode(e.target);
    if (target) {
      e.dataTransfer.effectAllowed = 'move';
      target.parentElement.ondragenter = this.onDragEnter;
      target.parentElement.ondragover = function(ev) {
        ev.preventDefault();
        return true;
      };
      const dragIndex = parseInt(target.rowIndex - 1);
      this.setState({ dragIndex, draggedIndex: dragIndex });
    }
  }

  onDragEnter = (e) => {
    const target = this.getTrNode(e.target);
    this.setState({
      draggedIndex: target ? parseInt(target.rowIndex - 1) : -1,
    });
  }

  onDragEnd = (e) => {
    const target = this.getTrNode(e.target);
    if (target) {
      target.setAttribute('draggable', false);
      target.ondragstart = null;
      target.ondragend = null;
      target.parentElement.ondragenter = null;
      target.parentElement.ondragover = null;
      this.changeRowIndex();
    }
  }

  getTrNode = (target) => {
    return closest(target, 'tr');
  }

  changeRowIndex = () => {
    const { onDragDrop } = this.props;
    const result = {};
    const currentState = this.state;
    result.dragIndex = result.draggedIndex = -1;
    if (
      currentState.dragIndex >= 0 &&
      currentState.dragIndex !== currentState.draggedIndex
    ) {
      const { dragIndex, draggedIndex } = currentState;
      if (onDragDrop) {
        onDragDrop({ dragIndex, draggedIndex });
      }
      result.dragIndex = -1;
      result.draggedIndex = -1;
      this.setState(result);
    }
  }

  render() {
    const { children, index, onRef, styleProps={}, ...restprops } = this.props;
    let classNames = '';
    if (this.state.dragIndex >= 0 &&
      this.state.dragIndex !== this.state.draggedIndex &&
      index === this.state.draggedIndex
    ) {
      classNames = `drag-target-line ${this.state.draggedIndex <
        this.state.dragIndex
        ? 'drag-target-top'
        : ''}`
    }

    return (
      <TableRow 
        ref={onRef} 
        onMouseDown={this.onMouseDown}
        className={`ui-sortable-handle permission-row ${classNames}`}
        draggable="false"
        style={styleProps}
        >
        {children}
      </TableRow>
    )
  }
}

export function closest(el, selector, rootNode) {
  rootNode = rootNode || document.body;
  const matchesSelector =
    el.matches ||
    el.webkitMatchesSelector ||
    el.mozMatchesSelector ||
    el.msMatchesSelector;

  while (el) {
    const flagRoot = el === rootNode;
    if (flagRoot || matchesSelector.call(el, selector)) {
      if (flagRoot) {
        el = null;
      }
      break;
    }
    el = el.parentElement;
  }
  return el;
};