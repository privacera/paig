import React from 'react';
import { observer } from 'mobx-react';

import {Grid} from '@material-ui/core';
import {FormHorizontal, FormGroupSwitch} from 'common-ui/components/form_fields';
import {STATUS} from 'common-ui/utils/globals';

const VVectorDBAccessForm = observer(({form, editMode}) => {

    const {userEnforcement, groupEnforcement} = form.fields;

    return (
        <FormHorizontal spacing={1}>
            <Grid item xs={12}>
                User/Group Access-Limited Retrieval
                <FormGroupSwitch
                    inputColAttr={{xs: 12, sm: 8}}
                    label="Enabled"
                    checked={userEnforcement.value === STATUS.enabled.value}
                    onChange={e => {
                        if (e.target.checked) {
                            userEnforcement.value = STATUS.enabled.value
                            groupEnforcement.value = STATUS.enabled.value
                        } else {
                            userEnforcement.value = STATUS.disabled.value
                            groupEnforcement.value = STATUS.disabled.value
                        }
                    }}
                    disabled={!editMode}
                />
            </Grid>
        </FormHorizontal>
  )
})

export default VVectorDBAccessForm;