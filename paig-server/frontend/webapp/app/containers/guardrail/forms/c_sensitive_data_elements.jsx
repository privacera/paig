import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import {extendObservable} from 'mobx';

import {Grid} from '@material-ui/core';

import f from 'common-ui/utils/f';
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {FEATURE_PERMISSIONS, PROMPT_REPLY_ACTION_TYPE} from 'utils/globals';
import FSModal from 'common-ui/lib/fs_modal';
import {VSensitiveDataElements} from 'components/guardrail/forms/v_sensitive_data_element';
import {VSensitiveDataElementForm} from 'components/guardrail/forms/v_sensitive_data_element_form';

@inject('sensitiveDataStore')
class CSensitiveDataElements extends Component {
    constructor(props) {
        super(props);

        this.cElements = f.initCollection({loading: false});

        this.cSensitiveData = f.initCollection();
        this.cSensitiveData.params = {
            size: 9999
        }

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.GUARDRAILS.PROPERTY);
    }
    componentDidMount() {
        this.fetchSensitiveData();
    }
    fetchSensitiveData = async() => {
        f.beforeCollectionFetch(this.cSensitiveData);

        try {
            const {models} = await this.props.sensitiveDataStore.fetchSensitiveData({
                params: this.cSensitiveData.params
            });

            models.forEach(m => {
                extendObservable(m, {
                    selected: false
                })
            })

            f.resetCollection(this.cSensitiveData, models);
        } catch(e) {
            f.handleError(this.cSensitiveData)(e);
        }

        this.nameDataMap = f.models(this.cSensitiveData).reduce((acc, model) => {
            acc[model.name] = model;
            return acc;
        }, {});

        let configs = this.props.getConfigs();
        let elements = [];
        if (configs) {
            configs.forEach(c => {
                elements.push({
                    name: c.category,
                    action: c.action,
                    description: this.nameDataMap[c.category]?.description || ''
                });
                if (this.nameDataMap[c.category]) {
                    this.nameDataMap[c.category].selected = true;
                }
            });
        }

        f.resetCollection(this.cElements, elements);
    }
    handleAdd = () => {
        this.sensitiveDataModal.show({
            title: 'Add Sensitive Data Element',
            btnOkText: 'Add'
        });
    }
    handleOnChange = () => {
        const models = f.models(this.cElements).map((model) => ({
            category: model.name,
            action: model.action
        }));
        this.props.onChange?.(models);
    }
    handleSave = () => {
        let elements = {};
        f.models(this.cSensitiveData).forEach((model) => {
            if (model.selected) {
                elements[model.name] = {
                    name: model.name,
                    description: model.description,
                    action: PROMPT_REPLY_ACTION_TYPE.REDACT.VALUE
                };
            }
        });

        f.models(this.cElements).forEach((model) => {
            if (elements[model.name]) {
                elements[model.name].action = model.action;
            }
        });

        f.resetCollection(this.cElements, Object.values(elements));

        this.handleOnChange();

        this.sensitiveDataModal.hide();
    }
    handleRemove = (model) => {
        f._confirm.show({
            title: `Confirm Remove`,
            children: <Fragment>Are you sure want to remove <b>{model.name}</b> category from elements?</Fragment>,
            btnOkVariant: "contained",
            btnOkColor: 'primary'
        })
        .then(confirm => {
            confirm.hide();

            const models = f.models(this.cElements).filter((m) => {
                let match = m.name === model.name;
                if (match && this.nameDataMap?.[model.name]) {
                    this.nameDataMap[model.name].selected = false;
                }
                return !match;
            });
            f.resetCollection(this.cElements, models);

            this.handleOnChange();
        }, () => {});
    }
    handleActionChange = (value, model) => {
        model.action = value;

        this.handleOnChange();
    }

    render() {
        return (
            <Fragment>
                <Grid container spacing={3}>
                    <AddButtonWithPermission
                        colAttr={{
                            xs: 12,
                            style: {
                                position: 'absolute',
                                right: '30px',
                                marginTop: '-55px'
                            }
                        }}
                        permission={this.permission}
                        onClick={this.handleAdd}
                        label="Add Element"
                        data-testid="add-sensitive-data-element"
                    />
                </Grid>

                <VSensitiveDataElements
                    data={this.cElements}
                    permission={this.permission}
                    handleActionChange={this.handleActionChange}
                    handleRemove={this.handleRemove}
                />
                <FSModal ref={ref => this.sensitiveDataModal = ref}
                    dataResolve={this.handleSave}
                    maxWidth="md"
                >
                    <VSensitiveDataElementForm
                        cSensitiveData={this.cSensitiveData}
                    />
                </FSModal>
            </Fragment>
        )
    }
}

export default CSensitiveDataElements;