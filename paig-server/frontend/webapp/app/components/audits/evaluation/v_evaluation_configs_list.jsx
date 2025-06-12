import React, {Component} from 'react';
import {observer, inject} from 'mobx-react';
import "styles/css/styles.css";

import {TableCell, TableRow, TableHead, TableBody, TableContainer} from '@material-ui/core';
import PlayCircleOutlineIcon from '@material-ui/icons/PlayCircleOutline';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import CircularProgress from '@material-ui/core/CircularProgress';

import {Utils} from 'common-ui/utils/utils';
import Table from 'common-ui/components/table';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import {PopperMenu} from 'common-ui/components/generic_components'
import MuiTable from '@material-ui/core/Table';
const moment = Utils.dateUtil.momentInstance();

@inject('evaluationStore')
@observer
class VEvaluationConfigTable extends Component{
  constructor(props) {
    super(props);
    this.state = {
      expandedRows: [],
      showCategoriesModal: false,
      selectedCategories: {},
      selectedCategoriesTitle: 'Categories'
    };
  }

  handleCategoriesClick = (model) => {
    try {
      // Parse categories if it's a string
      const categories = typeof model.categories === 'string' ? JSON.parse(model.categories) : model.categories;
      
      // Group categories by type
      const categoryTypeMap = categories.reduce((acc, category) => {
        const type = category.type;
        if (!acc[type]) {
          acc[type] = [];
        }
        acc[type].push(category.name);
        return acc;
      }, {});

      this.setState({
        showCategoriesModal: true,
        selectedCategories: categoryTypeMap,
        selectedCategoriesTitle: 'Categories'
      });
    } catch (error) {
      console.error('Error processing categories:', error);
    }
  }

  handleCloseCategoriesModal = () => {
    this.setState({ showCategoriesModal: false, selectedCategories: {} });
  }

  getCategoriesCount = (model) => {
    if (!model.categories) return '--';
    try {
      const categories = typeof model.categories === 'string' ? JSON.parse(model.categories) : model.categories;
      return (
        <span
          className="clickable-link"
          onClick={() => this.handleCategoriesClick(model)}
        >
          {Array.isArray(categories) ? categories.length : 0}
        </span>
      );
    } catch (e) {
      return '--';
    }
  }

  getHeaders = () => {
    let headers = ([
      <TableCell key="1">Name</TableCell>,
      <TableCell key="2">Applications</TableCell>,
      <TableCell key="3">Evaluation Purpose</TableCell>,
      <TableCell key="4">Categories</TableCell>,
      //- <TableCell key="4">Application Client</TableCell>,
      <TableCell key="5">Created</TableCell>,
      <TableCell key="6">Created By</TableCell>,
      <TableCell key="7">Runs</TableCell>,
      <TableCell width="100px" key="9">Actions</TableCell>
    ])

    return headers;
  }

  handleContextMenuSelection = (model, asUser) => {
    this.props.handleRun(model, asUser);
  }

  getRowData = (model) => {
    const {handleDelete, handleEdit, permission} = this.props;
    let rows = [
      <TableCell key="1">{model.name}</TableCell>,
      <TableCell key="2">{model.application_names || "--"}</TableCell>,
      <TableCell key="3">{model.purpose || "--"}</TableCell>,
      <TableCell key="4">{this.getCategoriesCount(model)}</TableCell>,
      //- <TableCell key="4">{model.application_client || "--"}</TableCell>,
      <TableCell key="5">{model.createTime ? moment(model.createTime).format(DATE_TIME_FORMATS.DATE_TIME_FORMAT_SHORT) : '--'}</TableCell>,
      <TableCell key="6">{model.owner || "--"}</TableCell>,
      <TableCell key="7">{model.eval_run_count}</TableCell>,
      <TableCell key="9" column="actions">
        <PopperMenu 
          buttonType="IconButton"
          label={ <CustomAnchorBtn
            tooltipLabel="Run"
            color="primary"
            icon={<PlayCircleOutlineIcon fontSize="small" />}
          />}  
          buttonProps={{size: 'small'}}
          menuOptions={[
            { 
              label: 'Run',
              onClick: () => this.handleContextMenuSelection(model, false)
            },
            {
              label: 'Run as user',
              onClick: () => this.handleContextMenuSelection(model, true),
              disabled: !model.application_names || model.application_names.includes(',')
            }
          ]}
        />
        <ActionButtonsWithPermission
          permission={permission}
          hideEdit={true}
          hideDelete={false}
          onDeleteClick={() => handleDelete(model)}
          onEditClick={() => handleEdit(model)}
        />
      </TableCell>
    ]
    return rows;
  }

  render() {
    const { data, pageChange } = this.props;
    return (
      <>
        <Table
          data={data}
          getHeaders={this.getHeaders}
          getRowData={this.getRowData}
          pageChange={pageChange}
          hasElevation={false}
        />
        {this.renderCategoriesModal()}
      </>
    )
  }

  renderCategoriesModal = () => {
    const { showCategoriesModal, selectedCategories, selectedCategoriesTitle } = this.state;
    const dotStyle = {
      display: 'inline-block',
      width: 10,
      height: 10,
      borderRadius: '50%',
      background: '#5c6f82',
      marginRight: 8,
      verticalAlign: 'middle'
    };
    const categoryStyle = {
      color: '#4d4949',
      fontWeight: 400,
      marginRight: 32,
      marginBottom: 8,
      display: 'inline-flex',
      alignItems: 'center',
      fontSize: 15
    };
    
    const dialogTitleStyle = {
      fontWeight: 500,
      fontSize: 24.5,
      color: '#1a1a1a'
    };
    const headerStyle = {
      color: '#4d4949',
      fontWeight: 700,
      fontSize: 16,
      borderBottom: '2px solid #e0e3e8',
      borderRight: '1px solid #e0e3e8',
      padding: '12px 16px',
      background: '#fff',
      minWidth: 200,
      textAlign: 'left'
    };
    const cellBorderStyle = {
      borderBottom: '1px solid #e0e3e8',
      borderRight: '1px solid #e0e3e8',
      padding: '12px 16px',
      background: '#fff'
    };
    const lastCellStyle = {
      borderBottom: '1px solid #e0e3e8',
      padding: '12px 16px',
      background: '#fff'
    };

    return (
      <Dialog open={showCategoriesModal} onClose={this.handleCloseCategoriesModal} maxWidth="md" fullWidth>
        <DialogTitle>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={dialogTitleStyle}>{selectedCategoriesTitle}</span>
            <IconButton 
              aria-label="close" 
              onClick={this.handleCloseCategoriesModal}
              style={{ position: 'absolute', right: 8, top: 8 }}
            >
              <CloseIcon />
            </IconButton>
          </div>
        </DialogTitle>
        <DialogContent>
          <TableContainer style={{ border: '1px solid #e0e3e8', borderRadius: 4 }}>
            <MuiTable style={{ borderCollapse: 'collapse', minWidth: 700 }}>
              <TableHead>
                <TableRow>
                  <TableCell style={headerStyle}>Type</TableCell>
                  <TableCell style={{ ...headerStyle, borderRight: 'none' }}>Categories</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(selectedCategories).map(([type, categories], idx, arr) => (
                  <TableRow key={type}>
                    <TableCell style={cellBorderStyle}>{type}</TableCell>
                    <TableCell style={lastCellStyle}>
                      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                        {categories.map((cat) => (
                          <span key={cat} style={categoryStyle}>
                            <span style={dotStyle}></span>
                            {cat}
                          </span>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
                {Object.keys(selectedCategories).length === 0 && (
                  <TableRow>
                    <TableCell colSpan={2} style={{ textAlign: 'center', padding: '20px' }}>
                      No categories found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </MuiTable>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={this.handleCloseCategoriesModal} color="primary">CLOSE</Button>
        </DialogActions>
      </Dialog>
    );
  }
}

export default VEvaluationConfigTable;
