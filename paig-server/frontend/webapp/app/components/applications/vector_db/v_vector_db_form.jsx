import React, {Fragment} from 'react';
import { observer } from 'mobx-react';

import {TextareaAutosize} from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';

import {Utils} from 'common-ui/utils/utils';
import {FormGroupInput, FormGroupSwitch, FormGroupSelect2} from 'common-ui/components/form_fields';
import {STATUS} from 'common-ui/utils/globals';
import {VECTOR_DB_TYPES} from 'utils/globals';

const VVectorDBForm = observer(({form, editMode}) => {
    const { id, name, description, status, type } = form.fields;

    return (
        <Fragment>
            {
                !id.value || editMode
                ?
                    <FormGroupSelect2
                        label="Type"
                        data={Object.values(VECTOR_DB_TYPES)}
                        labelKey="LABEL"
                        valueKey="TYPE"
                        variant="standard"
                        fieldObj={type}
                        data-testid="type"
                        disableClearable={true}
                    />
                :
                    <Grid item xs={12}>
                        <FormLabel>Type</FormLabel>
                        <div data-testid="type" style={{ marginBottom: '8px'}}>
                            {type.value}
                        </div>
                    </Grid>
            }
            
            {   
                !id.value || editMode
                ?
                    <FormGroupInput
                        required={true}
                        fieldObj={name}
                        textOnly={!!id.value}
                        label="Name"
                        variant="standard"
                        data-testid="name"
                    />
                :
                    <Grid item xs={12}>
                        <FormLabel>Name</FormLabel>
                        <div data-testid="name-text" style={{ marginBottom: '8px'}}>{name.value}</div>
                    </Grid>
            }
            {
                !id.value || editMode            
                ?
                    <FormGroupInput
                        fieldObj={description}
                        disabled={!!id.value && !editMode}
                        label="Description"
                        variant="standard"
                        rows={2}
                        multiline={true}
                        InputProps={{
                            inputComponent: TextareaAutosize
                        }}
                        data-testid="desc"
                    />
                :
                    <Grid item xs={12}>
                        <FormLabel>Description</FormLabel>
                        <div data-testid="desc-text">{description.value}</div>
                    </Grid>
            }
            <Grid item xs={12}>
                <FormLabel>Enabled</FormLabel>
                <FormGroupSwitch
                    showLabel={false}
                    disabled={!(!id.value || editMode)}
                    fieldObj={status}
                    inputColAttr={{ xs: 12}}
                    data-testid="status"
                />
            </Grid>
        </Fragment>
    );
})

const vector_db_form_def = {
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
    type: {
        defaultValue: VECTOR_DB_TYPES.MILVUS.TYPE
    },
    userEnforcement: {
        defaultValue: STATUS.disabled.value
    },
    groupEnforcement: {
        defaultValue: STATUS.disabled.value
    },
    status: {
        defaultValue: STATUS.enabled.value
    }
}

export {
    vector_db_form_def
}
export default VVectorDBForm;