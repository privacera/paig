/* library imports */
import React from 'react';
import { observer } from 'mobx-react';
import { observable } from 'mobx';
import map from 'lodash/map';

import Grid from '@material-ui/core/Grid';

/* other project imports */
import UISidebarTabsUtil from 'utils/ui_sidebar_tabs_util';
import { CATOGORIES_KEY_LABEL, FEATURE_PERMISSIONS } from 'utils/globals';
import stores from 'data/stores/all_stores';
import { Select2 } from 'common-ui/components/generic_components';
import { getUniqueIncludeExcludeCondition, includeExcludeFilteredResult } from 'common-ui/components/view_helpers'
import f from 'common-ui/utils/f';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import StructuredFilter from 'common-ui/lib/react-structured-filter/main';
import UiState from 'common-ui/data/ui_state';
import {configProperties} from 'utils/config_properties';
import { Utils } from 'common-ui/utils/utils';

const categories = getUniqueIncludeExcludeCondition();
let ckl = CATOGORIES_KEY_LABEL;
// params field name for fetching option list
let fieldList = [ckl.group_name.key, ckl.user_name.key, ckl.application.key, ckl.datazone_name.key, ckl.tags.key, /*ckl.purpose.key, ckl.ip.key, ckl.access.key, ckl.city.key, ckl.country_name.key, ckl.time_zone.key*/]
//params name shown on ui. will have field which is same as field on ui
let fieldListUi = [ckl.group_name.label, ckl.user_name.label, ckl.application.label, ckl.datazone_name.label, ckl.tags.label, /*ckl.purpose.label, ckl.ip.label, ckl.access.label, ckl.city.label, ckl.country_name.label, ckl.time_zone.label*/]

//observable list to store fields option list eg. observable({group_name_split : [], user_name: []});
let objForFieldList = {}
fieldListUi.forEach(field => objForFieldList[field] = []);

//optionList are exported
let optionList = observable(objForFieldList);

const checkAllReadPermission = (properties = []) => {
    return properties.some(property => {
        return permissionCheckerUtil.hasReadPermission(property.PROPERTY)
    });
}

const _fetchSearchFilterData = (field) => {
    const {
        DISCOVERY: {
            TAG, CLASSIFICATION, DATAZONE, PATTERNS, DICTIONARY, ML_MODEL
        }
    } = FEATURE_PERMISSIONS;
    /*
        SCHEMES permission is under crypto-ui and it's breaking the common-ui component. So hardcoded the SCHEMES permission for now.
        Need to revisit the implementation for saas/portal to resolve the issue.
    */
    const SCHEMES = { PROPERTY: 'encryption.scheme' };

    if (!UISidebarTabsUtil.isDiscoveryEnable?.()) {
        return null;
    }
    switch (field) {
        case ckl.user_name.key:
            return stores.alertsStore.getAllUsers();
        case ckl.application.key:
            const appStore = UiState.isCloudEnv() ? stores.dataSourceApplicationStore : stores.dictionaryApplicationStore;
            return appStore.getAllApplication().then(resp => {
			    return {
                    ...resp,
                    models: Utils.setApplicationNamesInModels(resp.models)
                };
            });
        case ckl.tags.key:
            if ((!UISidebarTabsUtil.isDiscoveryEnable?.() && !UISidebarTabsUtil.isCryptoEnable?.()) || (!configProperties.isDiscoveryEnabled?.() && !configProperties.isPegServiceActive?.())) {
                return null;
            }
            if(!checkAllReadPermission([TAG, CLASSIFICATION, DATAZONE, PATTERNS, DICTIONARY, ML_MODEL, SCHEMES])) {
                return null;
            }
            return stores.tagStore.searchTagDefs({ params: { size: 99999999, sort: 'name' } });
        default:
            return  stores.alertsStore.searchGroup({ params: { field: field } });
    }
}

const getOptionsList = async () => {
    let index = 0
    for (const field of fieldList) {
        try {
            const data = await _fetchSearchFilterData(field, index);
            if (!data) {
                optionList[fieldListUi[index]] = [];
                index++;
                continue;
            }
            if (ckl.application.key === field) {
                let models = data.models;
                models = models.map(m => ({
                    [ckl.application.key]: m.name
                }));
                optionList[ckl.application.key] = models;
            } else if (ckl.tags.key === field) {
                let list = data.models.map(m => ({
                    [ckl.tags.label]: m.name
                }));
                optionList[ckl.tags.label] = list;
            } else {
                optionList[fieldListUi[index]] = data.models;
            }
            index++;
        } catch (e) {
            console.log(e, "Failed to fetch options list.")
        }
    }
    return optionList;
}

//add options to search option
const addDropDownOptions = function (addDropDownOptions) {
    fieldListUi.forEach((field, i) => {
        let fieldObj = addDropDownOptions.find(obj => obj.category == field);
        if (fieldObj) {
            fieldObj.options = function () {
                const key = ckl.tags.key === fieldList[i] ? ckl.tags.label : fieldList[i];
                return map(optionList[field], key);
            }
        }
    });
}

const filterChanged = (filter, _vState, callback) => {
    _vState.searchFilterValue = filter;

    let filterConditionResult = includeExcludeFilteredResult(filter);

    callback && callback(filterConditionResult)
}

const VSearchComponent = observer(function VSearchComponent({ categoriesOptions, _vState, data = {}, params, callbacks }) {
    return (
        <div>
            <Grid container spacing={3} className="m-b-sm">
                <Grid item xs={12}>
                    <IncludeExcludeComponent
                        categoriesOptions={categoriesOptions || categories}
                        _vState={_vState}
                        callback={callbacks.handleTokenizerFilterChanged}
                    />
                </Grid>
            </Grid>
            <Grid container spacing={3} className="m-b-sm">
                <Grid item xs={12} md={6} className="m-b-xs">
                    {/* <div className="input-group"> */}
                        <Select2Component
                            promiseDataObj={data}
                            labelKey={'policy_name'}
                            valueKey={'policy_name'}
                            mutli={true}
                            valueObj={params}
                            valueAttr={'mustBe'}
                            placeholder={'Include Policies'}
                            callback={callbacks.handleFilterChanged}
                        />
                    {/* </div> */}
                </Grid>
                <Grid item xs={12} md={6} className="m-b-xs">
                    {/* <div className="input-group"> */}
                        <Select2Component
                            promiseDataObj={data}
                            labelKey={'policy_name'}
                            valueKey={'policy_name'}
                            mutli={true}
                            valueObj={params}
                            valueAttr={'mustNot'}
                            placeholder={'Exclude Policies'}
                            callback={callbacks.handleFilterChanged}
                        />
                    {/* </div> */}
                </Grid>
            </Grid>
        </div>
    );
});

const IncludeExcludeComponent = observer(function ({
    categoriesOptions = [], _vState = {}, callback, operator = ['is', 'is not'], onChange, placeholder = "Search", addDropOptions = true
}) {
    if (addDropOptions) {
        addDropDownOptions(categoriesOptions)
    }
    return (
        <div className="input-group includeFilter" data-track-id="structured-filter">
            <StructuredFilter
                placeholder={placeholder}
                options={categoriesOptions}
                customClasses={{
                    input: "filter-tokenizer-text-input",
                    results: "filter-tokenizer-list__container",
                    listItem: "filter-tokenizer-list__item",
                    textarea: "filter-tokenizer-textarea-input"
                }}
                operator={operator}
                onChange={(filter, event) => {
                    filter.forEach(el => el.value = el.value.trim());
                    if (event == 'renderEnd') { return }
                    onChange ? onChange(filter, event) : filterChanged(filter, _vState, callback);
                }}
                value={_vState.searchFilterValue && _vState.searchFilterValue.slice() || []}
            />
        </div>
    )
})

const Select2Component = observer(function ({ promiseDataObj, labelKey, valueKey, mutli = false, valueObj = {}, valueAttr, placeholder = "", callback }) {
    return (
        <Select2
            value={valueObj[valueAttr] ? valueObj[valueAttr].split(',').map((m) => m.split('"')[1]) : []}
            placeholder={placeholder}
            data={f.models(promiseDataObj)}
            onChange={(value) => {
                let newVal = value ? value.split(',').map(val => ("\"" + val + "\"")).join(',') : undefined;
                valueObj[valueAttr] = newVal;
                callback && callback();
            }}
            multiple={mutli}
            labelKey={labelKey}
            valueKey={valueKey}
            loading={f.isLoading(promiseDataObj)}
        />
    )
});

const IncludeComponent = observer(function ({ noOperator = false, categoriesOptions, _vState = {}, callback, onChange, operator = ["is"], allDropDownOptions = false }) {
    if (allDropDownOptions) {
        addDropDownOptions(categoriesOptions)
    }
    return (
        <div className="includeFilter" data-track-id="structured-filter">
            <StructuredFilter
                placeholder="Search"
                noOperator={noOperator}
                options={categoriesOptions}
                customClasses={{
                    input: "filter-tokenizer-text-input",
                    results: "filter-tokenizer-list__container",
                    listItem: "filter-tokenizer-list__item"
                }}
                operator={operator}
                onChange={(filter, event) => {
                    if (event == 'renderEnd') { return }
                    onChange ? onChange(filter, event) : filterChanged(filter, _vState, callback);
                }}
                value={_vState.searchFilterValue && _vState.searchFilterValue.slice()}
            />
        </div>
    )
})

export default VSearchComponent;
export {
    IncludeComponent,
    IncludeExcludeComponent,
    Select2Component,
    optionList,
    getOptionsList
}