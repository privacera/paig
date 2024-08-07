import React, {Component} from 'react';
import {observer, inject} from 'mobx-react';
import {observable} from 'mobx';

import { Grid, Button, Typography}  from "@material-ui/core";
import CircularProgress from "@material-ui/core/CircularProgress/CircularProgress";

import f from 'common-ui/utils/f';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import VVectorDBAccessForm from 'components/policies/v_vector_db_access_form';
import {vector_db_form_def} from 'components/applications/vector_db/v_vector_db_form';

@inject('vectorDBStore')
@observer
class CVectorDBAccessForm extends Component {
    @observable _vState = {
        editMode: false,
        saving: false
    }
    constructor(props) {
        super(props);

        this.form = createFSForm(vector_db_form_def);

        if (props.vectorDBModel) {
            this.form.refresh(props.vectorDBModel);
        }
    }
    handleEdit = () => {
        this._vState.editMode = true;
    }
    handleCancelEdit = () => {
        this._vState.editMode = false;
    }
    handleUpdate = async () => {
        const { vectorDBModel, postPermissionUpdate } = this.props;

        let data = Object.assign({}, vectorDBModel, this.form.toJSON());

        this._vState.saving = true;
        this.props.vectorDBStore.updateVectorDB(data)
            .then((response) => {
                f.notifySuccess('Permission updated successfully.');
                this._vState.editMode = false;
                this._vState.saving = false;
                postPermissionUpdate(response);
                this.form.refresh(response);
            }, (e) => {
                this._vState.saving = false;
                f.handleError()(e);
            });
    }

    render() {
        const { permission, vectorDBModel } = this.props;

        return (
            <Grid container spacing={3} style={{padding: '5px 15px'}} data-testid="access-card"
                data-track-id="vector-db-access-limited"
            >
                <Grid item sm={8} xs={12}>
                    <Typography variant="body1">
                        {vectorDBModel?.name}
                    </Typography>
                </Grid>
                <Grid item sm={4} xs={12} className="text-right">
                    {
                        !this._vState.editMode &&
                        <div style={{marginBottom: '7px'}}>
                            <ActionButtonsWithPermission
                                permission={permission}
                                onEditClick={this.handleEdit}
                                hideDelete={true}
                            />
                        </div>
                    }
                    {
                        this._vState.editMode &&
                        <div>
                            <Button
                                data-testid="edit-save-btn"
                                variant="contained"
                                color="primary"
                                className="m-r-sm"
                                size="small"
                                disabled={this._vState.saving}
                                onClick={this.handleUpdate}
                            >
                                {
                                    this._vState.saving &&
                                    <CircularProgress size="15px" className="m-r-xs" />
                                }
                                SAVE
                            </Button>
                            <Button
                                data-testid="edit-cancel-btn"
                                variant="outlined"
                                color="primary"
                                size="small"
                                onClick={this.handleCancelEdit}
                            >CANCEL</Button>
                        </div>
                    }
                </Grid>
                <VVectorDBAccessForm
                    ref={ref => this.policyFormRef = ref}
                    editMode={this._vState.editMode}
                    form={this.form}
                />
            </Grid>
        );
    }
}

export default CVectorDBAccessForm;