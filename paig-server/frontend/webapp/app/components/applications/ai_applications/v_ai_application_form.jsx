import React, {Fragment} from 'react';
import { observer } from 'mobx-react';

import {TextareaAutosize} from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';

import {Utils} from 'common-ui/utils/utils';
import {FormGroupInput, FormGroupSwitch, FormGroupSelect2} from 'common-ui/components/form_fields';
import {STATUS} from 'common-ui/utils/globals';
import {DEPLOYMENT_TYPE} from 'utils/globals';
import {configProperties} from 'utils/config_properties';
import {vectorDBLookUps} from 'components/policies/field_lookups';

const VectorDBAssociate = ({form, editMode}) => {
    if (!configProperties.isVectorDBEnable()) {
        return null;
    }
    const {id, vectorDBs} = form.fields;

    if (!id.value || editMode) {
        return (
            <FormGroupSelect2
                inputColAttr={{
                    xs: 12
                }}
                label="Associated VectorDB"
                fieldObj={vectorDBs}
                labelKey="label"
                valueKey="value"
                placeholder="Select Vector DB"
                variant="standard"
                triggerOnLoad={true}
                multiple={false}
                openText="Options"
                data-testid="associate-vector-db"
                loadOptions={(searchString, callback) => {
                    vectorDBLookUps(searchString, options => callback(options));
                }}
            />
        )
    }

    return (
        <Grid item xs={12}>
            <FormLabel>Associated VectorDB</FormLabel>
            <div data-testid="vector-name-text" style={{ marginBottom: '8px'}}>
                {vectorDBs.value?.join(', ') || 'None'}
            </div>
        </Grid>
    )
}

const VAIApplicationForm = observer(({form, editMode}) => {
    const { id, name, applicationKey, description, status, deploymentType, vectorDBs } = form.fields;

    return (
        <Fragment>
            {   
                !id.value || editMode
                ?
                <FormGroupInput
                    required={true}
                    fieldObj={name}
                    //textOnly={id.value && !editMode}
                    disabled={id.value && !editMode}
                    //showLabel={false}
                    label="Name"
                    variant="standard"
                    data-testid="app-name"
                />
                :
                <Grid item xs={12}>
                    <FormLabel>Name</FormLabel>
                    <div data-testid="app-name-text" style={{ marginBottom: '8px'}}>{name.value}</div>
                </Grid>
            }
            {
                /*id.value &&
                <FormGroupInput
                    inputColAttr={{
                        xs: 12,
                        sm: 6,
                        md: 5
                    }}
                    required={true}
                    fieldObj={applicationKey}
                    //textOnly={false}
                    disabled={true}
                    //showLabel={false}
                    label="API Key"
                    variant="standard"
                    data-testid="app-key"
                    InputProps={{
                        endAdornment: (
                            <CommandDisplay
                                key="command"
                                hideContent="true"
                                id="app-key"
                                command={applicationKey.value}
                            />
                        )
                    }}
                />*/
            }
            {
                !id.value || editMode            
                ?
                <FormGroupInput
                    fieldObj={description}
                    //textOnly={id.value && !editMode}
                    disabled={id.value && !editMode}
                    //showLabel={false}
                    label="Description"
                    variant="standard"
                    rows={2}
                    multiline={true}
                    InputProps={{
                        inputComponent: TextareaAutosize
                    }}

                    data-testid="app-desc"
                />
                :
                <Grid item xs={12}>
                    <FormLabel>Description</FormLabel>
                    <div className="break-word" data-testid="app-desc-text">{description.value}</div>
                </Grid>
            }
            <Grid item xs={12}>
                <FormLabel>Enabled</FormLabel>
                <FormGroupSwitch
                    showLabel={false}
                    disabled={!(!id.value || editMode)}
                    fieldObj={status}
                    inputColAttr={{ xs: 12}}
                    data-testid="app-status"
                />
            </Grid>

            <VectorDBAssociate
                form={form}
                editMode={editMode}
            />
            {/* Disable self enable */}
            {/* {
                configProperties.isShieldConfigEnable() && !id.value &&
                <Grid item xs={12}>
                    <FormLabel>Self Managed</FormLabel>
                    <FormGroupSwitch
                        showLabel={false}
                        disabled={!(!id.value || editMode)}
                        checked={deploymentType.value === DEPLOYMENT_TYPE.SELF_MANAGED.VALUE}
                        onChange={(e) => {
                            deploymentType.value = e.target.checked ? DEPLOYMENT_TYPE.SELF_MANAGED.VALUE : DEPLOYMENT_TYPE.CLOUD.VALUE;
                        }}
                        inputColAttr={{ xs: 12}}
                        data-testid="self-managed-status"
                    />
                </Grid>
            } */}
        </Fragment>
    );
})

const ai_application_form_def = {
    id: {},
    name: {
        defaultValue: "",
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                let length = (field.value || '').trim().length
                if (length > 0) {
                    if (length > 64) {
                        field._originalErrorMessage = 'Max 64 characters allowed!';
                        return false;
                    }

                    return Utils.characterValidation(field);
                }
                field._originalErrorMessage = 'Required!';
                return false;
            }
        }
    },
    applicationKey: {
        defaultValue: "",
        validators: {
            errorMessage: '',
            fn: (field, fields) => {
                /* let length = (fields.value || '').trim().length
                if (length > 0) {
                    return true;
                }
                return false; */
                return true;
            }
        }
    },
    description: {
        defaultValue: "",
        validators: {
            errorMessage: '',
            fn: (field) => {
                let length = (field.value || '').trim().length
                if (length > 5000) {
                    field._originalErrorMessage = 'Max 5000 characters allowed!';
                    return false;
                }
                field._originalErrorMessage = '';
                return true;
            }
        }
    },
    status: {
        defaultValue: STATUS.enabled.value
    },
    deploymentType: {
        defaultValue: DEPLOYMENT_TYPE.CLOUD.VALUE
    },
    vectorDBs: {
        defaultValue: []
    }
}

export {
    ai_application_form_def
}
export default VAIApplicationForm;