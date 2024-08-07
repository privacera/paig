import React, {Component} from 'react';
import {inject} from 'mobx-react';
import {action} from 'mobx';
import {groupBy, sortBy} from "lodash";

import {Grid} from '@material-ui/core';

import BaseContainer from 'containers/base_container';
import UiState from 'data/ui_state';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import {DEFAULTS} from 'common-ui/utils/globals';
import { PROMPT_REPLY_TYPE } from 'utils/globals';
import {configProperties} from 'utils/config_properties';
import {DateRangePickerComponent} from 'common-ui/components/filters';
import VSecurityAudits from 'components/audits/security/v_security_audits';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';

const CATEGORIES = {
    User: { multi: false, category: "User", type: "text", key: 'userId' },
    Application: { multi: false, category: "Application", type: "text", key: 'applicationName' },
    "Request Type": { multi: false, category: "Request Type", type: "text", key: 'requestType', options: () => ['Prompt', 'Context documents', 'Reply', 'Prompt to LLM']  },
    Result: { multi: false, category: "Result", type: "text", key: 'result', options: () => ['Masked', 'Allowed', 'Denied'] },
    Tag: { multi: false, category: "Tag", type: "text", key: 'trait' }
}

@inject('securityAuditsStore', 'aiApplicationStore', 'shieldConfigStore')
class CSecurityAudits extends Component {
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

        this.cAudits = f.initCollection();
        this.cAudits.params = {
            size: 120,
            sort: 'eventTime,threadSequenceNumber,desc',
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
        let {params} = this.cAudits;
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
        this.cAudits.params = data.params;
    }
    handleRefresh = () => {
        this.fetchSecurityAudits();
        this.fetchAIApplications();
        this.fetchShieldConfigUrl();
    }
    fetchSecurityAudits = () => {
        f.beforeCollectionFetch(this.cAudits);
        this.props.securityAuditsStore.fetchSecurityAudits({
            params: this.cAudits.params
        }).then(res => {
            f.resetCollection(this.cAudits, this.groupByThreadId(res.models), res.pageState);            
        },  f.handleError(this.cAudits));
    }
    fetchAIApplications = () => {
	    this.props.aiApplicationStore.getAIApplications({
	        params: {
                size: 100
            }
	    }).then((res) => {
            res.models.forEach(app => {
                this.applicationKeyMap[app.applicationKey] = app;
            });
        }, f.handleError());
    }
    fetchShieldConfigUrl = async () => {
        if (!configProperties.isShieldConfigEnable()) {
            return;
        }
        this._vState.shieldObj = await this.props.shieldConfigStore.getConfigUrl();
    }
    groupByThreadId = (models) => {
        let groupedData = groupBy(models, "threadId");
        let sortedGroupedData = Object.values(groupedData).map(group =>
            sortBy(group, ["eventTime", "threadSequenceNumber"])
        );
        return sortedGroupedData;
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
        this.cAudits.params.page = page || undefined;
        this.fetchSecurityAudits();
    }
    handleDateChange = (event, picker) => {
        this._vState.prevNextValueList = [''];
        this._vState.pageNumber = 0;
        delete this.cAudits.params.page;
        if (picker.startDate) {
            this.cAudits.params.fromTime = picker.startDate.valueOf();
            this.cAudits.params.toTime = picker.endDate.valueOf();

            this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
        } else {
            delete this.cAudits.params.fromTime;
            delete this.cAudits.params.toTime;
            this.dateRangeDetail.daterange = [];
        }
        this.dateRangeDetail.chosenLabel = picker.chosenLabel;

        this.fetchSecurityAudits();
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
        Object.assign(this.cAudits.params, params);

        this._vState.searchFilterValue = filter;
        this.fetchSecurityAudits();
    }
    render() {
        const {_vState, dateRangeDetail, handleDateChange} = this;

        return (
            <BaseContainer
                handleRefresh={this.handleRefresh}
                titleColAttr={{lg: 12, md: 12}}
            >
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={12} md={6} lg={7}>
                        <IncludeExcludeComponent
                            _vState={_vState}
                            categoriesOptions={Object.values(CATEGORIES)}
                            onChange={this.handleSearchByField}
                        />
                    </Grid>
                    <DateRangePickerComponent
                        colAttr={{ lg: 5, md: 6, sm: 12, xs: 12, className: 'text-right'}}
                        daterange={dateRangeDetail.daterange}
                        chosenLabel={dateRangeDetail.chosenLabel}
                        handleEvent={handleDateChange}
                    />
                </Grid>
                <VSecurityAudits
                    data={this.cAudits}
                    pageChange={this.handlePageChange}
                    _vState={_vState}
                    applicationKeyMap={this.applicationKeyMap}
                />
            </BaseContainer>
        )
    }
}

CSecurityAudits.defaultProps = {
    vName: 'securityAudits'
}

export default CSecurityAudits;