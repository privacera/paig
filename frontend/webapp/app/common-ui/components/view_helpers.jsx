import React from 'react';
import {Loader} from 'react-loaders'
import moment from 'moment-timezone';
import {has, isArray, uniqBy, uniq, forEach, each, isString} from 'lodash';

import {RESULT, CONDITIONS_CATEGORIES, ALERTS_COLOR, CATOGORIES_KEY_LABEL, REGEX,
  ACCESS_REQUEST_PROPERTY_MAPPER
} from 'utils/globals';
import UiState from 'data/ui_state';
import {TooltipOverlay} from 'common-ui/components/generic_components'
import {Utils} from 'common-ui/utils/utils';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';

/* Text Translation OR Loader */
const ttl = (size='sm', graphical = true, object, path ) => {
  /* Use _ so we can give deep path also.. a.b.c */
  if(has(object, path)){
    return tt(object[path]);
  }

  if (!graphical) {
      return "...";
  }
  return (
    <Loader type="line-scale" active size={size} />
  )
}

/* Text Translation (Globalization)*/
const tt = (str = '') => {
  return str;
  // TODO : Use some internationalizatoin here.
}

const toggleValue = (ref, attr) => {

    if (isArray(attr)) {
        attr.map((attrString) => {
            ref[attrString] = !ref[attrString];
        })
    } else if (isString(attr)) {
        ref[attr] = !ref[attr]
    }
}


const structuredFilterCondition = (stringVal, splitBy) => {
    let conditionList = stringVal.split(splitBy);
    return conditionList.map((condition) => {
      let split_condition = condition.split(' ');
      return {
        category: split_condition[0],
        operator: split_condition[1],
        value: split_condition.slice(2).join(' ')
      }
    })
}

const replaceStringValue = (ref, attr, search, replacement) => {
    if(!ref[attr]) {
      return;
    }
    ref[attr] = ref[attr].replace(new RegExp(search, 'g'), replacement);
}

const getUniqueIncludeExcludeCondition = () => {
  const alertsCategory = CONDITIONS_CATEGORIES.ALERTS_CATEGORY;
  const auditsCategory = CONDITIONS_CATEGORIES.AUDITS_CATEGORY;

  return uniqBy(alertsCategory.concat(auditsCategory), 'category');
}

const includeExcludeFilteredResults = (filter=[], columns=[], columnTitle={}) => {
  let includeOperatorList = ['==', 'is'];
  let excludeOperatorList = ['!=', 'is not'];

  let filters = [];
  let result = {}


  const filterTitle = Object.values(columnTitle);
  filter.forEach((obj) => {
    if(obj.value) {
      const foundFilterObj = filterTitle.find(item => item.title === obj.category);
      if (foundFilterObj) {
        filters.push({
          ...obj, category: foundFilterObj.key
        });
      } else {
        filters.push({...obj});
      }
    }
  });

  let includeFilter = filterMatchObj(filters, 'operator', includeOperatorList);
  let excludeFilter = filterMatchObj(filters, 'operator', excludeOperatorList);

  result.include = createKeyValueObj(includeFilter, 'category', 'value', columnTitle);
  result.exclude = createKeyValueObj(excludeFilter, 'category', 'value', columnTitle);

  return result;
}

const includeExcludeFilteredResult = (filter) => {
    
    let alertsCategory = CONDITIONS_CATEGORIES.ALERTS_CATEGORY;
    let auditsCategory = CONDITIONS_CATEGORIES.AUDITS_CATEGORY;
    let complianceCategory = CONDITIONS_CATEGORIES.COMPLIANCE_REPORT;
    let sparkEventCategory = CONDITIONS_CATEGORIES.SPARK_EVENT;
    let categories = getUniqueIncludeExcludeCondition();
    let includeOperatorList = ['==', 'is'];
    let excludeOperatorList = ['!=', 'is not'];

    let alertsFilter = [];
    let auditsFilter = [];
    let complianceFilter = [];
    let sparkEventFilter = [];
    let result = {
      alertFilters: {},
      auditFilters: {},
      complianceFilter: {},
      sparkEventFilter: {}
    }

    filter.forEach((obj) => {
        if(obj.value) {
            let cat = alertsCategory.find((cat) => {
                return cat.category == obj.category;
            })
            if(cat) {
                alertsFilter.push(obj)
            }
            cat = auditsCategory.find((cat) => {
                return cat.category == obj.category;
            })
            if(cat) {
                auditsFilter.push(obj)
            }
            cat = complianceCategory.find((cat) => {
                return cat.category == obj.category;
            })
            if(cat) {
                complianceFilter.push(obj)
            }
            cat = sparkEventCategory.find((cat) => {
                return cat.category == obj.category;
            })
            if(cat) {
                sparkEventFilter.push(obj);
            }
        }
    });

    let includeFilter = filterMatchObj(alertsFilter, 'operator', includeOperatorList);
    let excludeFilter = filterMatchObj(alertsFilter, 'operator', excludeOperatorList);

    result.alertFilters.include = createKeyValueObj(includeFilter, 'category', 'value');
    result.alertFilters.exclude = createKeyValueObj(excludeFilter, 'category', 'value');

    includeFilter = filterMatchObj(auditsFilter, 'operator', includeOperatorList);
    excludeFilter = filterMatchObj(auditsFilter, 'operator', excludeOperatorList);

    result.auditFilters.include = createKeyValueObj(includeFilter, 'category', 'value');
    result.auditFilters.exclude = createKeyValueObj(excludeFilter, 'category', 'value');

    includeFilter = filterMatchObj(complianceFilter, 'operator', includeOperatorList);
    excludeFilter = filterMatchObj(complianceFilter, 'operator', excludeOperatorList);

    result.complianceFilter.include = createKeyValueObj(includeFilter, 'category', 'value');
    result.complianceFilter.exclude = createKeyValueObj(excludeFilter, 'category', 'value');

    includeFilter = filterMatchObj(sparkEventFilter, 'operator', includeOperatorList);
    excludeFilter = filterMatchObj(sparkEventFilter, 'operator', excludeOperatorList);

    result.sparkEventFilter.include = createKeyValueObj(includeFilter, 'category', 'value');
    result.sparkEventFilter.exclude = createKeyValueObj(excludeFilter, 'category', 'value');

    return result;
}

const filterMatchObj = (list, attr, valueList) => {
  return list.filter((obj) => {
    return valueList.some( value => {
      return obj[attr] == value;
    })
  });
}

const createKeyValueObj = (list, attr, value, columnTitle={}) => {
  let val;
  return list.map((obj) => {
    val = obj[value];

    if(obj[attr] == CATOGORIES_KEY_LABEL.result.label) {
      let result = Object.values(RESULT).find(o =>  o.label.toUpperCase() === obj.value.toUpperCase());
      if(result){
        val = result.value;
      }
    }
    const columnObj = columnTitle && columnTitle[obj[attr]];
    if([CATOGORIES_KEY_LABEL.resource.label, 'resource_arn'].includes(obj[attr]) || (columnObj && obj[attr] === columnObj.key && columnObj.partialSearch)) {
      val = "*"+ val +"*";
    }

    if(obj[attr] == CATOGORIES_KEY_LABEL.isDecrypted.label) {
      val = val == 'true' ? "1" : "0";
    }

    if (CATOGORIES_KEY_LABEL[obj[attr]]) {
      return {
        [CATOGORIES_KEY_LABEL[obj[attr]].key]: val
      }
    }
    return {
      [obj[attr]]: val
    }
  });
}

const restoreTabState = (context, _vName) => {
  let data = UiState.getStateData(_vName)
    if (!data) {
      return;
    }
    Object.assign(context, {
      tabsState: data.tabsState
    });
}

const getDescriptiveAlert = (alert) => {
    let obj = {};
    if(alert.low > 0) {
        obj.low = `Low alert generated if ${alert.function} exceeds ${alert.low}%`;
    }
    if(alert.medium > 0) {
        obj.medium = `Medium alert generated if ${alert.function} exceeds ${alert.medium}%`;
    }
    if(alert.high > 0) {
        obj.high = `High alert generated if ${alert.function} exceeds ${alert.high}%`;
    }
    return obj;
}

const makePolicyString = (policyModel, cDictionaryApplication) => {
  let tags = policyModel.getOrStringFromArray(policyModel.tagsArray);
  let purpose = policyModel.getOrStringFromArray(policyModel.purposeArray);
  let access = policyModel.getOrStringFromArray(policyModel.accessArray);
  let conditions = policyModel.conditions;
  let application = policyModel.getApplicationNameString(cDictionaryApplication);

  return (
    <span>
      {`${access ? access : 'All'} attempts`}
      {application &&
        <span> in application(s)
          {wrapTooltip(application)}
        </span>
      }
      {purpose &&
        <span> for
          {wrapTooltip(purpose)} purpose
        </span>
      }
      {tags &&
        <span>, where data is
          {wrapTooltip(tags)}
        </span>
      }
      {conditions &&
        <span> due to
          {wrapTooltip(conditions)}
        </span>
      }
    </span>
  )
}

const permissionMap = new Map();
const makeReasonString = ({
  message=null, dateRangeDetail, model={}, FEATURE_PERMISSIONS={}, DATAZONE_POLICY_TYPE={}
}) => {
  let dzPermission = permissionMap.get('dz');
  let classificationPermission = permissionMap.get('classificationPermission');
  if (!dzPermission) {
    dzPermission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.DISCOVERY?.DATAZONE?.PROPERTY);
    permissionMap.set('dz', dzPermission);
  }
  if (!classificationPermission) {
    classificationPermission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.DISCOVERY?.CLASSIFICATION?.PROPERTY);
    permissionMap.set('classificationPermission', classificationPermission);
  }
  let msg = message;
  let disallowed_list = '';
  if (message && isArray(message)) {
    let [alertMsg] = message;
    if (typeof alertMsg == "string") {
      alertMsg = Utils.parseJSON(alertMsg);
      let resource = null;
      let srcResource = null;
      let srcList = alertMsg.disallowed_list;
      let app = model.application && model.application[0];
      if (alertMsg.resource) {
        resource = Utils.smartTrim(alertMsg.resource, 50);
        if (dateRangeDetail && dateRangeDetail.daterange) {
          let [fromDate, toDate] = dateRangeDetail.daterange;
          if (permissionCheckerUtil.checkHasReadPermission(classificationPermission)) {
            resource = <a href={formResourceDetailLink(alertMsg.resource, app || "-", fromDate, toDate, dateRangeDetail.chosenLabel)}>{resource}</a>
          } else {
            resource = <b>{resource}</b>
          }
        }
      }
      let alertSrcResource = alertMsg.src_resources;
      if (model.alert_key == DATAZONE_POLICY_TYPE.MONITORING_OUTBOUND.VALUE) {
        if (alertMsg.dst_resources) {
          alertSrcResource = alertMsg.dst_resources;
          srcList = alertMsg.whitelisted_list || srcList;
        } else {
          srcList = 'Outbound'
        }
      }
      if (alertSrcResource) {
        let srcResourceList = [];
        let res = alertSrcResource.split(',');
        if (model.src_app_name) {
          app = model.src_app_name;
        }
        res.forEach(resource => {
          let resourceTrim = Utils.smartTrim(resource, 50);
          if (dateRangeDetail && dateRangeDetail.daterange) {
            let [fromDate, toDate] = dateRangeDetail.daterange;
            if (permissionCheckerUtil.checkHasReadPermission(classificationPermission)) {
              srcResourceList.push(<a key={resource} className="alert-resource-name" href={formResourceDetailLink(resource, app || "-", fromDate, toDate, dateRangeDetail.chosenLabel)}>{resourceTrim}</a>);
            } else {
              srcResourceList.push(<strong key={resource} className="alert-resource-name">{resourceTrim}</strong>);
            }
          }
        })
        srcResource = srcResourceList;
      }
      let datazone = null;
      if (alertMsg.dz_name) {
        let dzLink = <a className="alert-resource-name" href={`#/datazone/detail/${alertMsg.dz_name}`}><strong>{alertMsg.dz_name}</strong></a>;
        if (!permissionCheckerUtil.checkHasReadPermission(dzPermission)) {
          dzLink = <strong className="alert-resource-name"><strong>{alertMsg.dz_name}</strong></strong>;
        }
        let msg = 'in';
        if (model.alert_key == DATAZONE_POLICY_TYPE.MONITORING_OUTBOUND.VALUE) {
          msg = 'from';
        }
        datazone = (<span> is not allowed {msg} {dzLink}</span>)
      }
      let fileTypeSize = '';
      let list = [];
      if (alertMsg.disallowed_filetype) {
        list.push(`filetype:  ${alertMsg.disallowed_filetype}`)
      }
      if (alertMsg.filesize) {
        list.push(`filesize:  ${Utils.formatBytes(alertMsg.filesize, 1)}`)
      }
      if (alertMsg.max_filesize_exceeded) {
        list.push(`maxfilesize:  ${Utils.formatBytes(alertMsg.max_filesize_exceeded, 1)}`)
      }
      fileTypeSize = list.join(", ");
      let movedTo = '';
      if (model.alert_key == DATAZONE_POLICY_TYPE.WORK_FLOW.VALUE) {
        let quarantineLocation = '';
        if (alertMsg.quarantine_location) {
          quarantineLocation = (<span>: <strong>{alertMsg.quarantine_location}</strong></span>)
        }
        movedTo = (<span>, file will be moved to quarantine folder {quarantineLocation}</span>);
      } else if (model.alert_key == DATAZONE_POLICY_TYPE.WORK_FLOW_EXPUNGE.VALUE) {
        movedTo = [];
        if (alertMsg.quarantine_rec_count != null) {
          let records = (+alertMsg.quarantine_rec_count) > 1 ? 'records' : 'record';
          movedTo.push(<span key="rec_count">, found <strong>{alertMsg.quarantine_rec_count}</strong> {records} in violation and</span>);
        }
        let quarantineLocation = '';
        if (alertMsg.quarantine_location) {
          quarantineLocation = (<span>: <strong>{alertMsg.quarantine_location}</strong></span>)
        }
        movedTo.push(<span key="location"> will be moved to quarantine folder {quarantineLocation}</span>);
      }

      msg = (
        <span>
          {srcList && <strong>{srcList}</strong>}
          {
            fileTypeSize
            ? <span><strong> ({fileTypeSize})</strong></span>
            : srcResource && <span><strong> ({srcResource})</strong></span>
          }
          {datazone}
          {resource && <span><strong> ({resource})</strong></span>}
          {movedTo}
        </span>
      );
    }
  }
  return msg;
            //`<b>${alertMsg.disallowed_list}</b> <b>(${alertMsg.resource})</b> is not allowed in <b>${alertMsg.dz_name}</b>`;
}

const wrapTooltip = (string) => {
    let splitArr = string.split(', ');
    let initial = splitArr.slice(0, 4).join(', ');
    let remaining = splitArr.slice(4).join(', ');

      return (
        <strong> {initial}
            {remaining &&
                <TooltipOverlay tooltipContent={remaining}>
                   <span>,<span className="policy-info">...</span></span>
                </TooltipOverlay>
            }
        </strong>
      )
}

const formUserDetailLink = (access, name,startDate,endDate,label) => {
  return `#/access/detail/${access}/${name}/${startDate && startDate.toJSON()}/${endDate && endDate.toJSON()}/${label}`;
}

const formResourceDetailLink = (resourceName, applicationName="-", startDate, endDate, label=null, deleted=false) => {

  resourceName = resourceName && Utils.replaceSlashToEncodedChar(resourceName);

  if (deleted) {
    return `#/resource/detail/${resourceName}/${applicationName}/deleted`;
  } else {
    return `#/resource/detail/${resourceName}/${applicationName}`;
  }
}

const generateHistogramData = (graphData) => {
  return graphData.models.map((graphData) => {
    return {
      key: graphData.name,
      values: graphData.dataCount.map((object) => {
        return {
          x: Utils.dateUtil.getMomentObject(object.name),
          y: parseFloat(object.value)
        }
      }),
      color: ALERTS_COLOR[graphData.name.toUpperCase()].value
    }
  });
}

const generateLineChartData = (graphData) => {

  let mainObj = [];

  graphData.models.forEach((graphData) => {

    let name = graphData.name;
    var dataCount = graphData.dataCount;

    var values = dataCount.map((data, i) => {
      return {
        x: moment(data.name),
        y: parseInt(data.value, 10) || 0
      }
    });

    mainObj.push({
      values: values,
      key: name == "1" ? 'Count' : name
    })
  });
  return mainObj;
}

const generateTopAlertsData = (graphData) => {

  let mainObj = [];

  graphData.models.forEach((graphData) => {

    let name = graphData.name;
    var dataCount = graphData.dataCount;

    for (var i = 0; i < dataCount.length; i++) {
      var valueObj = {
        label: name,
        value: parseInt(dataCount[i].value, 10) || 0
      }

      var ret = mainObj.find((obj) => {
        return obj.key == dataCount[i].name.toUpperCase();
      });
      if (ret) {
        ret.values.push(valueObj);
      } else {
        mainObj.push({
          key: dataCount[i].name.toUpperCase(),
          values: [valueObj],
          color: ALERTS_COLOR[dataCount[i].name.toUpperCase()].value
        });
      }
    }
  });
  return mainObj;
}

const getClosestElement = (el, selector) => {
    var matchesFn;

    // find vendor prefix
    ['matches','webkitMatchesSelector','mozMatchesSelector','msMatchesSelector','oMatchesSelector'].some(function(fn) {
        if (typeof document.body[fn] == 'function') {
            matchesFn = fn;
            return true;
        }
        return false;
    })

    var parent;

    // traverse parents
    while (el) {
        parent = el.parentElement || el.parentNode;
        if (parent && parent[matchesFn] && parent[matchesFn](selector)) {
            return parent;
        }
        el = parent;
    }

    return null;
}

const getDataAttributes = (attributes) => {
  var d = {},
    re_dataAttr = /^data\-(.+)$/;

  each(attributes, (attr) => {
    if (re_dataAttr.test(attr.nodeName)) {
      var key = attr.nodeName.match(re_dataAttr)[1];
      d[key] = attr.nodeValue;
    }
  })

  return d;
}

const getLogFilePath = (string='', r=REGEX.LOG_FILE) => {
  let matchingList = Utils.findMatchingElements(string, 'argument');
  let regexForTag = new RegExp('<[^>]+>', 'gi');
  let logFilePath = '';

  matchingList.forEach(ele => {
    if(r.test(ele)) {
      logFilePath = ele.replace(regexForTag, '').split('=')[1];
    }
  });
  return logFilePath;
}

const isJson = (str) => {
  try {
    JSON.parse(str);
  } catch (e) {
    return false;
  }
  return true;
}

const JOIN_SPLIT = ','
const convertTagsToUpperCase = (tags=[]) => {
  if (isArray(tags)) {
    tags = tags.join(JOIN_SPLIT);
  }

  if (tags.toUpperCase) {
     tags = tags.toUpperCase();
     tags = tags ? tags.split(JOIN_SPLIT) : [];
     return uniq(tags);
  }

  return false;
}

const makeFeedActivityData = (list=[], topLevelTotal=0) => {
  let order = ['high', 'medium', 'low'];

  list.map((obj) => {
    let total = obj.dataCount && obj.dataCount.reduce((prev, obj) => {
      return (+prev) + (+obj.value);
    }, 0);
    let dataCount = [];
    topLevelTotal = topLevelTotal || total;
    obj.dataCount.forEach((dcObj) => {
      dcObj.totalAlertCount = total;
      dcObj.topTotal = topLevelTotal;
      dcObj.per = (+dcObj.value / topLevelTotal) * 100;
      dcObj.alertClassName = ALERTS_COLOR[dcObj.name.toUpperCase()].className;
      dcObj.progressStyle = ALERTS_COLOR[dcObj.name.toUpperCase()].progressStyle;
      dataCount[order.indexOf(dcObj.name.toLowerCase())] = dcObj
    })
    obj.total = total;
    obj.topLevelTotal = topLevelTotal;
    obj.dataCount = dataCount;
  });

  return list;
}
const makeAccessDeniedTagProgressData = (list=[], topLevelTotal=0) => {
  let order = [{Allowed:'success'},{Denied:'danger'}];

  list.map((obj) => {
    let dataCount = [];
    topLevelTotal = topLevelTotal || obj.total;
    if(obj.pivot && obj.pivot.length){
      let allowedObj = obj.pivot.find((ob)=>ob.name == 'Allowed');
      let deniedObj = obj.pivot.find((ob)=>ob.name == 'Denied');
      if(allowedObj){
        dataCount.push({per:(+allowedObj.value / topLevelTotal) * 100,progressStyle:'primary'})
      }
      if(deniedObj){
        dataCount.push({per:(+deniedObj.value / topLevelTotal) * 100,progressStyle:'danger'})
      }
    }else{
      dataCount.push({per:(+obj.value / topLevelTotal) * 100,progressStyle:'primary'})
    }
    obj.dataCount = dataCount;
  });

  return list;
}

const createBrush = (options) => {
    let {svg, fromDate, toDate, callback} = options;
    let svgElem = svg,
        elem = svgElem.querySelectorAll('.nv-axis .nv-wrap');
    if (elem.length == 0 || elem.length == undefined) {
        return;
    }

    let height = (elem.item(0).getBBox().height == 0) ? 250 : elem.item(0).getBBox().height + 2,
        width = (elem.item(0).getBBox().width == 0) ? 250 : elem.item(0).getBBox().width


    let x = d3.time.scale().range([0, width]).domain([moment(fromDate), moment(toDate)])
    let brush = d3.svg.brush()
        .x(x)
        .on('brushend', brushend);

    let brushElem = svgElem.querySelector('.nv-groups');

    svg = d3.select(brushElem)
        .insert("g", ":first-child")
        .attr("transform", "translate(" + elem.item(0).getBBox().x + ",-9)");


    svg.append("g")
        .attr("class", "x-brush brush")
        .call(brush)
        .selectAll("rect")
        .attr("y", 6)
        .attr("height", height);

    function brushend() {
        let brushValue = brush.extent();

        if (moment(brushValue[0]).isSame(brushValue[1])) {
            return;
        }

        if (callback) {
            callback({
                startDate: Utils.dateUtil.getMomentObject(brushValue[0]),
                endDate: Utils.dateUtil.getMomentObject(brushValue[1]),
                chosenLabel: 'Custom Range'
            });
        }

        this.parentNode ? this.parentNode.remove() : '';
        let xBrush = brushElem.querySelector('.x-brush');
        if(xBrush) {
            xBrush.parentNode.remove();
        }
        hideTooltip();
    }
}

const hideTooltip = () => {
  if (document.getElementsByClassName('nvtooltip').length) {
    d3.selectAll('.nvtooltip').remove();
  }
}

const graphXAxisBreak = (svg) => {
    var insertLinebreaks = function(element) {
        var el = d3.select(element);
        var words = element.textContent.split('-');
        element.textContent = '';
        forEach(words, (word, i) => {
            var tspan = el.append('tspan').text(word);
            if (i > 0)
                tspan.attr('x', 0).attr('dy', '19');
        })
    };
    let tickElements = svg.querySelectorAll('.tick, .nv-axisMaxMin-x')
    if (tickElements[0] && tickElements[0].getElementsByTagName('text')[0] && tickElements[0].getElementsByTagName('text')[0].textContent.split('-').length > 1) {
        forEach(tickElements, (element) => {
            insertLinebreaks(element.getElementsByTagName('text')[0]);
        })
    }
}

const matchText = (text, regex) => text && regex && text.match(regex);

const isHive = (text) => matchText(text || "", REGEX.HIVE_APP_NAME);

const makeDBResourcePath = (db, table, column) => {
  let path = "";
  if(db) {
    path = db
  }
  if(table) {
    path = `${path}/${table}`;
  } else if (column) {
    path = `${path}/*`;
  }
  if(column) {
    path = `${path}/${column}`;
  }
  return path;
}

const seperateDbResource = (resource="") => {
  let resourceObj = {};
  let splitResource = resource.split('/');

  resourceObj.database = splitResource[0] || "";
  resourceObj.table = splitResource[1] || "";
  resourceObj.column = splitResource[2] || "";

  return resourceObj;
}

const metricsDateRangePickerRange = () => {
  let ranges = {
    'Last 10 Mins': Utils.dateUtil.getLast10Mins(),
    'Last 30 Mins': Utils.dateUtil.getLast30Mins(),
    'Last 1 Hour': Utils.dateUtil.getLast1HourRange(),
    'Last 12 Hours': Utils.dateUtil.getLast12HoursRange(),
    'Last 24 Hours': Utils.dateUtil.getLast24HoursRange(),
    'Today': Utils.dateUtil.getTodayRange(),
    'Yesterday': Utils.dateUtil.getYesterdayRange(),
    'Last 7 Days': Utils.dateUtil.getLast7DaysRange()
  }
  Object.defineProperty(ranges, 'Last 10 Mins', {
    get: function() {
      return Utils.dateUtil.getLast10Mins();
    }
  });
  Object.defineProperty(ranges, 'Last 30 Mins', {
    get: function() {
      return Utils.dateUtil.getLast30Mins();
    }
  });
  Object.defineProperty(ranges, 'Last 1 Hour', {get: function() { return Utils.dateUtil.getLast1HourRange();}});
  Object.defineProperty(ranges, 'Last 12 Hours', {get: function() { return Utils.dateUtil.getLast12HoursRange();}});
  Object.defineProperty(ranges, 'Last 24 Hours', {get: function() { return Utils.dateUtil.getLast24HoursRange();}});
  return ranges;
}

const getDiscoveryEnableAppDropdown = (options=[]) => {
  options.forEach(app => {
      if (app.enableDiscovery) {
          delete app.disabled;
      } else {
          app.disabled = true;
      }
  });
  return options;
}

const prepareDBdetailsFromResourceName = (resourceName) => {
  const response = {};

  if (resourceName && typeof resourceName === "string") {
    const resourceNameArr = resourceName.split('/');
    response.databaseName = resourceNameArr[0].split('.')[0];
    response.schemaName = resourceNameArr[0].split('.')[1] || null;
    response.tableName = resourceNameArr[1];
  };

  return response;
}

const prepareResourceArrForTagRoleRequests = (resources, resourceType) => {

  const resArr = ACCESS_REQUEST_PROPERTY_MAPPER[resourceType] ? resources[0][ACCESS_REQUEST_PROPERTY_MAPPER[resourceType].propName].split(',') : [];

  if(resArr.length > 1){
    return resArr.map(r => ({
      [ACCESS_REQUEST_PROPERTY_MAPPER[resourceType].propName]: r,
      requestState: resources[0].requestState
    }));
  };

  return resources;
}

export {
    ttl,
    tt,
    toggleValue,
    structuredFilterCondition,
    replaceStringValue,
    getUniqueIncludeExcludeCondition,
    includeExcludeFilteredResult,
    includeExcludeFilteredResults,
    filterMatchObj,
    createKeyValueObj,
    restoreTabState,
    getDescriptiveAlert,
    formUserDetailLink,
    formResourceDetailLink,
    generateHistogramData,
    generateLineChartData,
    generateTopAlertsData,
    makePolicyString,
    makeReasonString,
    getClosestElement,
    getDataAttributes,
    getLogFilePath,
    isJson,
    convertTagsToUpperCase,
    makeFeedActivityData,
    createBrush,
    graphXAxisBreak,
    hideTooltip,
    matchText,
    isHive,
    makeDBResourcePath,
    seperateDbResource,
    metricsDateRangePickerRange,
    makeAccessDeniedTagProgressData,
    getDiscoveryEnableAppDropdown,
    prepareDBdetailsFromResourceName,
    prepareResourceArrForTagRoleRequests
}