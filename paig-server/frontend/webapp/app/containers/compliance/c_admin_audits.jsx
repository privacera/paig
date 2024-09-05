import React, {Component} from 'react';
import {inject} from 'mobx-react';
import {action} from 'mobx';

import BaseContainer from 'containers/base_container';
import UiState from 'data/ui_state';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import {DEFAULTS} from 'common-ui/utils/globals';
import {DateRangePickerComponent} from 'common-ui/components/filters';
import VAdminAudits from 'components/compliance/v_admin_audits';

@inject('adminAuditsStore')
class CAdminAudits extends Component {
    constructor(props) {
        super(props);

        this.dateRangeDetail = {
            daterange: Utils.dateUtil.getLast7DaysRange(),
            chosenLabel: 'Last 7 Days'
        }

        this.cAdminAudits = f.initCollection();
        this.cAdminAudits.params = {
            size: DEFAULTS.DEFAULT_PAGE_SIZE,
            sort: 'logTime,transactionSequenceNumber,desc',
            fromTime: this.dateRangeDetail.daterange[0].valueOf(),
            toTime: this.dateRangeDetail.daterange[1].valueOf(),
            "includeQuery.transactionSequenceNumber": 1
        }

        this.restoreState();
    }
    componentDidMount() {
        this.handleFetch();
    }
    componentWillUnmount() {
        let {_vState, dateRangeDetail} = this;
        let {params} = this.cAdminAudits;
        let {vName} = this.props;
        let data = JSON.stringify({_vState, params, dateRangeDetail});
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
          _vState: data._vState,
          dateRangeDetail: data.dateRangeDetail
        });
        this.cAdminAudits.params = data.params;
    }
    handleFetch = () => {
        f.beforeCollectionFetch(this.cAdminAudits);
        this.props.adminAuditsStore.fetchComplianceAudits({
            params: this.cAdminAudits.params
        })
        .then(f.handleSuccess(this.cAdminAudits), f.handleError(this.cAdminAudits));
    }
    handleRefresh = () => {
        this.handleFetch();
    }
    handlePageChange = () => {
        this.handleRefresh();
    }
    handleDateChange = (event, picker) => {
        delete this.cAdminAudits.params.page;
        if (picker.startDate) {
            this.cAdminAudits.params.fromTime = picker.startDate.valueOf();
            this.cAdminAudits.params.toTime = picker.endDate.valueOf();
    
            this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
        } else {
            delete this.cAdminAudits.params.fromTime;
            delete this.cAdminAudits.params.toTime;
            this.dateRangeDetail.daterange = [];
        }
        this.dateRangeDetail.chosenLabel = picker.chosenLabel;
    
        this.handleRefresh();
    }
    render() {
        const {dateRangeDetail, handleDateChange} = this;

        return (
            <BaseContainer
                handleRefresh={this.handleRefresh}
                titleColAttr={{lg: 7, md: 5}}
                headerChildren={
                    <DateRangePickerComponent
                        colAttr={{ lg: 5, md: 7, sm: 12, xs: 12, className: 'text-right'}}
                        daterange={dateRangeDetail.daterange}
                        chosenLabel={dateRangeDetail.chosenLabel}
                        handleEvent={handleDateChange}
                    />
                }
            >
                <VAdminAudits
                    data={this.cAdminAudits}
                    pageChange={this.handlePageChange}
                />
            </BaseContainer>
        )
    }
}

CAdminAudits.defaultProps = {
    vName: 'adminAudits'
}

export default CAdminAudits;