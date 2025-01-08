import React, {Component} from 'react';
import {inject, observer} from 'mobx-react';
import {action} from 'mobx';
import {groupBy, sortBy} from "lodash";
import {Grid} from '@material-ui/core';
import BaseContainer from 'containers/base_container';
import UiState from 'data/ui_state';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import { PROMPT_REPLY_TYPE } from 'utils/globals';
import {DateRangePickerComponent} from 'common-ui/components/filters';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';
import VEvaluationReportTable from 'components/applications/evaluation/v_evaluation_reports_list';
import {  Button } from "@material-ui/core";


const CATEGORIES = {
    ID: { multi: false, category: "ID", type: "text", key: 'eval_id' },
    User: { multi: false, category: "User", type: "text", key: 'owner' },
    Purpose: { multi: false, category: "Purpose", type: "text", key: 'owner' },
    Application: { multi: false, category: "Application", type: "text", key: 'application_name' },
    Status: { multi: false, category: "Status", type: "text", key: 'result', options: () => ['In Progress', 'Completed', 'Failed'] }
}

@inject('evaluationStore')
@observer
class CEvaluationReportsList extends Component {

    state = {
        showIframe: false,
        iframeUrl: null, // URL for iframe content
    };

    _vState = {
        searchFilterValue: [],
        shieldObj: null,
        showNextPage: null,
        prevNextValueList:[''],
        pageNumber: 0,
    }
    constructor(props) {
        super(props);

        this.dateRangeDetail = {
            daterange: Utils.dateUtil.getLast7DaysRange(),
            chosenLabel: 'Last 7 Days'
        }

        this.cEvalReports = f.initCollection();
        this.cEvalReports.params = {
            size: 120,
            sort: 'create_time,desc',
            fromTime: this.dateRangeDetail.daterange[0].valueOf(),
            toTime: this.dateRangeDetail.daterange[1].valueOf()
        }

        this.applicationKeyMap = {};

        this.restoreState();
    }
    componentDidMount() {
        this.handleRefresh();
    }
    componentWillUnmount() {
        let {dateRangeDetail, _vState} = this;
        let {params} = this.cEvalReports;
        let {vName} = this.props;
        let data = JSON.stringify({params, dateRangeDetail, _vState});
        UiState.saveState(vName, data);
    }
    @action
    restoreState() {
        let data = UiState.getStateData(this.props.vName)
        if (!data) {
          return;
        }
        if (data.dateRangeDetail.daterange.length) {
            data.dateRangeDetail.daterange[0] = Utils.dateUtil.getMomentObject(data.dateRangeDetail.daterange[0]);
            data.dateRangeDetail.daterange[1] = Utils.dateUtil.getMomentObject(data.dateRangeDetail.daterange[1]);
        }
        Object.assign(this, {
          dateRangeDetail: data.dateRangeDetail,
          _vState: data._vState
        });
        this.cEvalReports.params = data.params;
    }
    handleRefresh = () => {
        this.fetchEvaluationReports();
    }
    fetchEvaluationReports = () => {
        f.beforeCollectionFetch(this.cEvalReports);
        this.props.evaluationStore.fetchEvaluationReports({
            params: this.cEvalReports.params
        }).then(res => {
            console.log('res', res);
            f.resetCollection(this.cEvalReports, res.models, res.pageState);            
        },  f.handleError(this.cEvalReports));
    }

    handlePageChange = (isPrevious) => {
        let page = this._vState.pageNumber;
        if (isPrevious) {
            page--;
            this._vState.prevNextValueList.pop()
        } else {
            page++;
            this._vState.prevNextValueList.push(page)
        }
        this._vState.pageNumber = page
        this.cEvalReports.params.page = page || undefined;
        this.fetchEvaluationReports();
    }
    handleDateChange = (event, picker) => {
        this._vState.prevNextValueList = [''];
        this._vState.pageNumber = 0;
        delete this.cEvalReports.params.page;
        if (picker.startDate) {
            this.cEvalReports.params.fromTime = picker.startDate.valueOf();
            this.cEvalReports.params.toTime = picker.endDate.valueOf();

            this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
        } else {
            delete this.cEvalReports.params.fromTime;
            delete this.cEvalReports.params.toTime;
            this.dateRangeDetail.daterange = [];
        }
        this.dateRangeDetail.chosenLabel = picker.chosenLabel;

        this.fetchEvaluationReports();
    }
    handleSearchByField = (filter, event) => {
        this._vState.prevNextValueList = [''];
        this._vState.pageNumber = 0;
        let params = {
            page: undefined
        };
        Object.values(CATEGORIES).forEach(obj => {
            params['includeQuery.' + obj.key] = undefined;
            params['excludeQuery.' + obj.key] = undefined;
        })

        filter.forEach((item) => {
            let obj = CATEGORIES[item.category];
            let prefix = item.operator == 'is' ? 'includeQuery' : 'excludeQuery';
            let value = item.value;
            if (obj) {
                if (obj.category && ['User', 'Application'].includes(obj.category)) {
                    if (!value.startsWith('*')) {
                        value = `*${value}`;
                    }
                    if (!value.endsWith('*')) {
                        value = `${value}*`;
                    }
                }
                if (obj.key === 'result') {
                    value = value.toLowerCase();
                } else if (obj.key === 'requestType') {
                    value = value.toLowerCase();
                    if (value === 'context documents') {
                        value = PROMPT_REPLY_TYPE.RAG;
                    } else if (value === 'prompt to llm') {
                        value = PROMPT_REPLY_TYPE.ENRICH_PROMPT;
                    }
                }        
                params[`${prefix}.${obj.key}`] = value;
            }        
        });
        Object.assign(this.cEvalReports.params, params);

        this._vState.searchFilterValue = filter;
        this.fetchEvaluationReports();
    }

    handleDelete = (model) => {
        console.log('handle dleete called', model);
    }

    handleView = (model) => {
        console.log(model);
        this.setState({
            showIframe: true,
            iframeUrl: model.report_url + "/report?evalId=" + model.report_id, // Assuming `viewUrl` contains the URL to be displayed
        });
        console.log("iframeUrl",  model.report_url + "/report?evalId=" + model.report_id);
    };

    handleBack = () => {
        this.setState({
            showIframe: false,
            iframeUrl: null,
        });
    };

    render() {
        const {_vState, dateRangeDetail, handleDateChange} = this;
        const { showIframe, iframeUrl } = this.state;
        

        return (
            <BaseContainer
                handleRefresh={this.handleRefresh}
                titleColAttr={{ lg: 12, md: 12 }}
            >
                {!showIframe ? (
                    <>
                        <Grid container spacing={3}>
                            <Grid item xs={12} sm={12} md={6} lg={7}>
                                <IncludeExcludeComponent
                                    _vState={_vState}
                                    categoriesOptions={Object.values(CATEGORIES)}
                                    onChange={this.handleSearchByField}
                                />
                            </Grid>
                            <DateRangePickerComponent
                                colAttr={{ lg: 5, md: 6, sm: 12, xs: 12, className: 'text-right' }}
                                daterange={dateRangeDetail.daterange}
                                chosenLabel={dateRangeDetail.chosenLabel}
                                handleEvent={handleDateChange}
                            />
                        </Grid>
                        <VEvaluationReportTable
                            data={this.cEvalReports}
                            pageChange={this.handlePageChange}
                            _vState={_vState}
                            applicationKeyMap={this.applicationKeyMap}
                            handleDelete={this.handleDelete}
                            handleView={this.handleView}
                        />
                    </>
                ) : (
                    <div>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={this.handleBack}
                            style={{ marginBottom: '10px' }}
                        >
                            Back
                        </Button>
                        <iframe
                            src={iframeUrl}
                            style={{ width: '100%', height: '80vh', border: 'none' }}
                            title="View Details"
                        />
                    </div>
                )}
            </BaseContainer>
        );
    }
}

CEvaluationReportsList.defaultProps = {
    vName: 'evaluationReports'
}

export default CEvaluationReportsList;