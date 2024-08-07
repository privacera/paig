import {SCHEDULE_FOR} from 'utils/globals';
import stores from 'data/stores/all_stores';
import MScanSchedule from 'common-ui/data/models/m_scan_schedule';
import MReportConfig from 'common-ui/data/models/m_report_config';
import {FIELDS_STR, SCHEDULE_TYPE} from 'common-ui/utils/globals';
import {Utils} from 'common-ui/utils/utils';

class CommonUtil {
  params = {};
  dateAs = 'relative';
  enableDateRange = true;
  dateFormat='MM-DD-YY HH:mm';
  dateRanges = Utils.dateRangePickerRange();
  enableDate(enable=true) {
    this.enableDateRange = enable;
  }
  isDateEnable() {
    return this.enableDateRange;
  }
  getDateRange() {
    return this.dateRangeDetail;
  }
  getParams() {
    return this.params;
  }
  createDefaultDateRange() {
    this.dateRangeDetail = {
      daterange: Utils.dateUtil.getLast7DaysRange(),
      chosenLabel: 'Last 7 Days'
    }
  }
  setDateParams() {
    if (!this.isDateEnable()) {
      this.params.from = undefined;
      this.params.to = undefined;
      return;
    }
      this.params.from = Utils.dateUtil.toJSON(this.dateRangeDetail.daterange[0]);
      this.params.to = Utils.dateUtil.toJSON(this.dateRangeDetail.daterange[1]);    
  }
  getParam = (attr) => {
    return this.params[attr];
  }
  setParam = (attr, value) => {
    this.params[attr] = value || undefined;
  }
  setDateRange = (event, picker) => {
    this.dateRangeDetail = this.dateRangeDetail || {};
    this.dateRangeDetail.chosenLabel = picker.chosenLabel;
    if(picker.endDate && picker.startDate) {
      this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
      this.enableDate(true);
      this.setDateParams();
    } else {
      this.enableDate(false);
      this.setDateParams();
    }
  }
  resetDateRange() {
    this.createDefaultDateRange();
    this.setDateParams();
  }
  resetParams = () => {
    this.params = {};
  }
  addQuotesToCommaSeperatedString = (str='') => {
    str = str ? str.split(',') : [];
    return str.map(s => `"${s}"`).join(',');
  }
  replaceQuote(str='', replaceWith='') {
    if (typeof str != 'string') {
      return '';
    }
    return str.replace(new RegExp('\"', 'g'), replaceWith);
  }
  setDateAs(dateAs) {
    if (!dateAs) {
      dateAs = 'relative';
    }
    this.dateAs = dateAs;
  }
  setDefaultDateRanges(ranges=Utils.dateRangePickerRange()) {
    this.dateRanges = ranges;
  }
  getDefaultDateRanges() {
    return this.dateRanges;
  }
  calculateChosenLabel(from, to) {
    let dateRanges = this.getDefaultDateRanges();
    let chosenLabel = 'Custom Range';
    for (let key in dateRanges) {
      let dateRange = dateRanges[key];
      if (dateRange[0].isSame(from) && dateRange[1].isSame(to)) {
        chosenLabel = key;
        break;
      }
    }
    return chosenLabel;
  }
  getDateRangeFromParams(params={}) {
    let dateRangeDetail = {
      startDate: null,
      endDate: null,
      chosenLabel: 'Custom Range'
    }
    if (params.dateAs == 'absolute' || params.chosenLabel == 'Custom Range' ) {
      if (params.from) {
        dateRangeDetail.startDate = Utils.dateUtil.getMomentObject(params.from);
      }
      if (params.to) {
        dateRangeDetail.endDate = Utils.dateUtil.getMomentObject(params.to)
      }

      dateRangeDetail.chosenLabel = this.calculateChosenLabel(params.from, params.to);

      // if (params.chosenLabel) {
      //   dateRangeDetail.chosenLabel = params.chosenLabel;
      // }
    } else {
      //relative
      
      let labelAs = params.chosenLabel || 'Last 7 Days';
      let date = this.getDefaultDateRanges()[labelAs]
      if (date && this.isDateEnable()) {
        dateRangeDetail.startDate = date[0];
        dateRangeDetail.endDate = date[1];
        dateRangeDetail.chosenLabel = labelAs;
      }
    }
    return dateRangeDetail;
  }
  setDateRangeFromParams(params) {
    this.setDateRange(null, this.getDateRangeFromParams(params));
  }
  getDateFormat() {
    return this.dateFormat;
  }
  setDateFormat(dateFormat) {
    this.dateFormat = dateFormat
  }
  fromToDateString(dateFormat=this.getDateFormat()) {
    let dateRangeDetail = this.getDateRange();
    return `${Utils.dateUtil.getTimeZone(dateRangeDetail.daterange[0], dateFormat)} to ${Utils.dateUtil.getTimeZone(dateRangeDetail.daterange[1], dateFormat)}`;
  }
}

class ReportUtil extends CommonUtil {
    configId = null;
    configObj = null;
  
    setConfigId = (configId) => {
      this.configId = configId;
    }
    getConfigId() {
      return this.configId;
    }
    getConfig() {
      return this.configObj;
    }
    setConfig = (config) => {
      this.configObj = config;
    }
    collectReportDataFromForm = (form, _vState, reportType='', saveAs, advancedFilter, includeExcludeQuery) => {
      let data = form.toJSON();
      if (saveAs == 'new') {
        data.id = undefined;
        data.scheduleId = undefined;
      }
      if (!data.id) {
        data.id = undefined;
      }
  
      data.scheduledFor = SCHEDULE_FOR.DASHBOARD_REPORT.label;
      data.lastScheduled = null;
      data.isAll = !!data.isAll;
      switch(data.scheduleType) {
        case SCHEDULE_TYPE.ONCE.value:
        case SCHEDULE_TYPE.DAILY.value:
          data.day = undefined;
          data.month = undefined;
          break;
        case SCHEDULE_TYPE.WEEKLY.value:
          data.month = undefined;
          if (data.isAll) {
            data.day = undefined;
          }
          break;
        case SCHEDULE_TYPE.MONTHLY.value:
          if (data.isAll) {
            data.month = undefined;
          }
          break;
      }
      let scheduleId = data.scheduleId || undefined;
      let {id, schedulerName, reportName, description, emailTo, emailMessage, scheduleReport} = data;
      data.id = undefined;
      data.schedulerName = undefined
      data.reportName = undefined;
      data.description = undefined;
      data.emailTo = undefined;
      data.emailMessage = undefined;
      data.scheduleId = undefined;
      data.scheduleReport = undefined;
      data.paramJson = undefined;
  
      let scheduleInfo = new MScanSchedule({
        ...data, id: scheduleId, name: schedulerName
      })
      let paramJson = {
        reportType,
        dateAs: this.enableDateRange ? _vState.dateAs : '',
        from: this.params.from,
        to: this.params.to,
        chosenLabel: this.enableDateRange ? this.dateRangeDetail.chosenLabel : '',
        filterType: _vState.filterType || 'basic',
        advancedFilter: advancedFilter || '',
        includeExcludeQuery: includeExcludeQuery || undefined,
        quickDateFilter: _vState.quickDateFilter || '',
        tags: _vState.tags || '',
        topTag: _vState.topTag || 'Top 5',
        datazone: _vState.datazone || '',
      }
      this.addParamsIfHasOwnProperty(paramJson, 'tags', _vState, FIELDS_STR.ALL_TAGS_STR);
      this.addParamsIfHasOwnProperty(paramJson, 'datazone', _vState, FIELDS_STR.DATAZONE_STR);
      this.addParamsIfHasOwnProperty(paramJson, 'application', _vState, FIELDS_STR.APP_NAME);
      this.addParamsIfHasOwnProperty(paramJson, 'level', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'resource', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'excludeResources', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'excludeDescription', _vState);
      if(_vState.resource) {
        this.addParamsIfHasOwnProperty(paramJson, 'searchType', _vState);
      }
      this.addParamsIfHasOwnProperty(paramJson, 'alertKey', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'policyName', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'showAllTags', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'groupPartFiles', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'groupTables', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'appCode', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'taggedResource', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'unTaggedResource', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'failedResource', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'excludedResource', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'deletedResource', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'user', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'excludeServiceUsers', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'quickDateFilter', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'topTag', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'scanId', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'searchByLocation', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'resourceListSelected', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'showLogs', _vState);
      if(_vState.scanType) {
        this.addParamsIfHasOwnProperty(paramJson, 'scanType', _vState)
      }
  
      //DataBricks Param
      this.addParamsIfHasOwnProperty(paramJson, 'result', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'accessType', _vState);
      this.addParamsIfHasOwnProperty(paramJson, 'workspaceId', _vState );
      this.addParamsIfHasOwnProperty(paramJson, 'cluster', _vState );
      this.addParamsIfHasOwnProperty(paramJson, 'accountId', _vState );
  
      //DataZone Report Param
      this.addParamsIfHasOwnProperty(paramJson, 'tagAttributes', _vState );
  
      this.addParamsIfHasOwnProperty(paramJson, 'graphLegendState', _vState );
      paramJson = JSON.stringify(paramJson);
  
      let config = new MReportConfig({
        id: id || undefined,
        reportName,
        description,
        paramJson,
        emailTo,
        emailMessage,
        status: data.status,
        scheduleInfo: scheduleReport ? scheduleInfo : undefined
      });
  
      return config;
    }
    addParamsIfHasOwnProperty(addToObj={}, storeFieldName='', fields={}, attr='') {
      if (!attr && storeFieldName) {
        attr = storeFieldName;
      }
      if(fields.hasOwnProperty(attr)) {
        addToObj[storeFieldName] = fields[attr];
      }
      return addToObj;
    }
    fetchConfig() {
      let configId = this.getConfigId();
      if (configId) {
        return stores.discoveryStore.getReportConfig(configId, {
          noCache: true
        });
      }
      return null;
    }
  
    saveReportConfig(config) {
      if (!config) {
        return;
      }
      if (config.id) {
        return stores.discoveryStore.updateReportConfig(config);
      }
  
      return stores.discoveryStore.createReportConfig(config);
    }
  
    resetData() {
      this.resetParams();
      this.resetDateRange();
      this.setConfigId(null);
      this.setConfig(null);
    }
  
    reloadFilter(refInstance) {
      refInstance = ((refInstance && refInstance.wrappedInstance) || (refInstance))
      if (refInstance) {
        refInstance.reload && refInstance.reload();
      }
    }
    getStringFromSet(data) {
      if (!data instanceof Set) {
        return '';
      }
      return Array.from(data).join(',');
    }
  
    mergeString = (existing='', newString='') => {
      let set = new Set();
      existing && existing.split(',').forEach(e => set.add(e));
      newString && set.add(newString);
      return this.getStringFromSet(set);
    }
  }

  export {
    ReportUtil,
    CommonUtil
  }