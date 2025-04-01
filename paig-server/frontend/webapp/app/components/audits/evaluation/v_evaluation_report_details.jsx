import React, {Component, Fragment, useEffect} from "react";
import {observer} from "mobx-react";
import {Box, Grid, Paper, Typography, TableCell} from "@material-ui/core";

import f from 'common-ui/utils/f';
import Table from "common-ui/components/table";
import {EVAL_REPORT_CATEGORIES} from 'utils/globals';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';
import {CustomButtonGroup} from 'common-ui/components/filters';
import {FormGroupSelect2} from 'common-ui/components/form_fields';
import {SEVERITY_MAP} from 'utils/globals';

const PaperCard = (props) => {
  const { children, boxProps={}, paperProps={} } = props;
  return (
    <Box {...boxProps}>
      <Paper {...paperProps}>
        <Box p={2}>{children}</Box>
      </Paper>
    </Box>
  );
};

@observer
class VEvaluationReportDetails extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      selectedValue: 'Show All', 
      selectedCategory: null, // Default selected
    };
  }

  getHeaders = () => {
    const { data } = this.props;
    const dataModels = f.models(data) || [];
    const responseHeaders = dataModels[0]?.responses?.map((response, index) => (
      <TableCell key={`response-${index}`}>{`Response (${response.application_name})`}</TableCell>
    )) || [];

    return (
      <Fragment>
        <TableCell key="category" className='min-width-100'>Category</TableCell>
        <TableCell key="type" className='min-width-100'>Type</TableCell>
        <TableCell key="prompt" className='min-width-200'>Prompt</TableCell>
        {responseHeaders}
      </Fragment>
    );
  }

  // Align responses with the respective application_name columns
  getRows = (model) => {
    const { data } = this.props;
    const dataModels = f.models(data) || [];
    const appNames = dataModels[0]?.responses?.map(response => response.application_name) || [];

    const responseCells = appNames.map((appName, index) => {
      const appResponse = model.responses?.find(response => response.application_name === appName);
      return (
        <TableCell key={`response-${appName}-${index}`}>
          {appResponse ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '4px' }}>
              <div style={{ display: 'flex', gap: '4px' }}>
              <Typography
                style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  backgroundColor: appResponse.status === 'PASSED' ? '#d4edda' :
                    appResponse.status === 'FAILED' ? '#f8d7da' : '#fff3cd',
                  color: appResponse.status === 'PASSED' ? '#155724' :
                    appResponse.status === 'FAILED' ? '#721c24' : '#856404',
                  fontSize: '12px',
                  fontWeight: 500
                }}
              >
                {appResponse.status || '--'}
              </Typography>
              {(appResponse.status === 'FAILED' || appResponse.status === 'ERROR') && <span><Typography
                style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  backgroundColor: SEVERITY_MAP?.[appResponse.category_severity]?.COLOR || SEVERITY_MAP?.HIGH?.COLOR,
                  fontSize: '12px',
                  fontWeight: 500
                }}
              >
                {SEVERITY_MAP?.[appResponse.category_severity]?.LABEL || SEVERITY_MAP?.HIGH?.LABEL}
              </Typography></span>
            }
            </div>
              {appResponse.response || '--'}
              {(appResponse.status === 'FAILED' || appResponse.status === 'ERROR') && appResponse.failure_reason && (
                <Box
                  style={{
                    padding: '8px',
                    borderRadius: '4px',
                    backgroundColor: appResponse.status === 'FAILED' ? '#f8d7da' : '#FFFAEB',
                  }}
                >
                  <Typography
                    style={{
                      fontSize: '12px',
                      fontWeight: 500
                    }}
                  >
                    {appResponse.failure_reason}
                  </Typography>
                </Box>
              )}
            </div>
          ) : (
            '--'
          )}
        </TableCell>
      );
    });

    return (
      <Fragment>
        <TableCell key="category">
          {model.responses?.[0]?.category || '--'}
        </TableCell>
        <TableCell key="type">
          {model.responses?.[0]?.category_type || '--'}
        </TableCell>
        <TableCell key="prompt">
          {model.prompt || '--'}
        </TableCell>
        {responseCells}
      </Fragment>
    );
  };


  handleCategorySelection = (selectedValue) => {
    this.setState({ selectedCategory: selectedValue }, () => {
        this.props.handleCategoryChange(selectedValue);
    });
  };  

  render() {
    const { _vState, data, handlePageChange, handleSearchByField, handleToggleChange, handleCategoryChange, reportCategories } = this.props;
    const { selectedCategory } = this.state;
    return (
      <Fragment>
        <PaperCard boxProps={{ mb: 2 }}>
          <Grid container spacing={3}>
            <Grid item xs={6} sm={6} md={6} lg={6}>
              <IncludeExcludeComponent
                _vState={_vState}
                categoriesOptions={Object.values(EVAL_REPORT_CATEGORIES)}
                onChange={handleSearchByField}
              />
            </Grid>
            <Grid item xs={6} sm={6} md={6} lg={6}>
              <Grid container spacing={3} justify="flex-end">
                <Grid item xs={3} sm={5} md={5} lg={5}>
                    <FormGroupSelect2
                        // inputColAttr={{ xs: 12, sm: 4 }}
                        required={false}
                        showLabel={false}
                        value={selectedCategory}
                        data={reportCategories?.category?.map(category => ({ name: category }))}
                        labelKey={'name'}
                        valueKey={'name'}
                        onChange={(newValue) => this.handleCategorySelection(newValue)}
                        data-testid="category-filter"
                        multiple={false}
                        disableClearable={false}
                        placeholder={'Filter Category'}
                    />
                </Grid>
                <Grid item>
                      <CustomButtonGroup buttonList={['Show All', 'Passed', 'Failed']} value={this.state.selectedValue}  onClick={handleToggleChange} size='small'/>
                </Grid>
              </Grid>
            </Grid>
          </Grid>

          <Table
            className="eval-table"
            tableClassName="eval-table"
            data={data}
            getHeaders={this.getHeaders}
            getRowData={this.getRows}
            hasElevation={false}
            pageChange={handlePageChange}
          />
        </PaperCard>
      </Fragment>
    );
  };
}

export default VEvaluationReportDetails;
