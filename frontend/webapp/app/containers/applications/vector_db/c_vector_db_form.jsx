import React, {Component, Fragment} from 'react';
import {observer, inject} from 'mobx-react';
import {observable} from 'mobx';

import { Grid, Button, Typography, Paper, Box }  from "@material-ui/core";
import CircularProgress from "@material-ui/core/CircularProgress/CircularProgress";

import UiState from 'data/ui_state';
import VVectorDBForm, {vector_db_form_def} from 'components/applications/vector_db/v_vector_db_form';
import f from 'common-ui/utils/f';
import {CanUpdate, ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import {createFSForm} from 'common-ui/lib/form/fs_form';

@inject('vectorDBStore')
@observer
class CVectorDBForm extends Component {
    @observable _vState = {
        editMode: false,
        saving: false
    }
    constructor(props) {
        super(props);

        const model = props.model || {};

        this.form = createFSForm(vector_db_form_def);

        if (model.id) {
            this.form.refresh(model);
        }
    }
    handleEdit = () => {
        this._vState.editMode = true;
    }
    handleCancelEdit = () => {
        this._vState.editMode = false;
        this.form.refresh(this.props.model);
    }

    handleCreate = async () => {
        await this.form.validate();
        if (!this.form.valid) {
            return;
        }
        let data = this.form.toJSON();
        delete data.id;

        try {
            this._vState.saving = true;

            let response = await this.props.vectorDBStore.createVectorDB(data);
            f.notifySuccess("The Vector DB created successfully");
            this.props.handlePostCreate?.(response);
        } catch(e) {
            this._vState.saving = false;
            f.handleError()(e);
        }
    }
    handleUpdate = async () => {
        await this.form.validate();
        if (!this.form.valid) {
            return;
        }
        let data = this.form.toJSON();
        let {model} = this.props;
        data = Object.assign({}, model, data);

        try {
            this._vState.saving = true;
            await this.props.vectorDBStore.updateVectorDB(data)
            f.notifySuccess("The Vector DB updated successfully");
            this.props.handlePostUpdate?.(data.id);
        } catch(e) {
            this._vState.saving = false;
            f.handleError()(e);
        }
    }

    render() {
        const {model, permission, handleCancel} = this.props;
        const {handleCreate, handleUpdate} = this;

        return (
            <Fragment>
                <Box component={Paper} className={`m-t-sm ${ model?.id ? 'm-b-md' : 'm-b-sm'}`}>
                    <Grid container spacing={3} style={{padding: '5px 15px'}}>
                        <Grid item sm={6} xs={12}>
                            <Typography variant="h6" component="h2">
                                Information
                            </Typography>
                        </Grid>
                        <Grid item sm={6} xs={12} className="text-right">
                            {
                                model?.id != null && !this._vState.editMode &&
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
                                        variant="contained"
                                        color="primary"
                                        className="m-r-sm"
                                        size="small"
                                        disabled={this._vState.saving}
                                        onClick={handleUpdate}
                                        data-testid="edit-save-btn"
                                    >
                                        {
                                            this._vState.saving &&
                                            <CircularProgress size="15px" className="m-r-xs" />
                                        }
                                        SAVE
                                    </Button>
                                    <Button
                                        variant="outlined"
                                        color="primary"
                                        size="small"
                                        onClick={this.handleCancelEdit}
                                        data-testid="edit-cancel-btn"
                                    >CANCEL</Button>
                                </div>
                            }
                        </Grid>
                        <VVectorDBForm
                            form={this.form}
                            editMode={this._vState.editMode}
                        />
                    </Grid>
                </Box>
                {
                    model?.id == null &&
                    <CanUpdate permission={permission}>
                        <Grid container spacing={3} className="m-t-md">
                            <Grid item xs={12}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    className="m-r-sm"
                                    disabled={this._vState.saving}
                                    onClick={handleCreate}
                                    data-testid="create-app-btn"
                                    data-track-id="create-vector-db-save-btn"
                                >
                                    {
                                        this._vState.saving &&
                                        <CircularProgress size="18px" className="m-r-xs" />
                                    }
                                    CREATE
                                </Button>
                                <Button
                                    data-testid="cancel-btn"
                                    variant="contained"
                                    onClick={handleCancel}
                                    data-track-id="create-vector-db-cancel-btn"
                                >
                                    CANCEL
                                </Button>
                            </Grid>
                        </Grid>
                    </CanUpdate>
                }
            </Fragment>
        );
    }
}

export default CVectorDBForm;