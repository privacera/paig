import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';

import BaseContainer from 'containers/base_container';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import VVectorDB from 'components/applications/vector_db/v_vector_db';
import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import {PaginationComponent} from 'common-ui/components/generic_components';

@inject('vectorDBStore')
class CVectorDB extends Component {
	constructor(props) {
		super(props);

		this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.VECTOR_DB.PROPERTY);

		this.cVectorDBs = f.initCollection();
		this.cVectorDBs.params = {
            size: DEFAULTS.DEFAULT_PAGE_SIZE,
            sort: 'createTime,desc'
        };
	}

	componentDidMount() {
	    this.getVectorDBs();
	}
	getVectorDBs = () => {
	    f.beforeCollectionFetch(this.cVectorDBs)
	    this.props.vectorDBStore.getVectorDBs({
	        params: this.cVectorDBs.params
	    }).then(f.handleSuccess(this.cVectorDBs), f.handleError(this.cVectorDBs));
	}
	handleRefresh = () => {
        this.getVectorDBs();
    }
    handleVectorDBCreate = () => {
        this.props.history.push('/vector_db/create');
    }
    handleVectorDBEdit = (id) => {
        this.props.history.push('/vector_db/' + id);
    }
    handleDeleteVectorDB = (model) => {
        f._confirm.show({
            title: 'Confirm Delete',
			children: <Fragment>Are you sure you want to delete <b>{model.name}</b> vector DB?</Fragment>,
			btnCancelText: 'Cancel',
			btnOkText: 'Delete',
			btnOkColor: 'secondary',
			btnOkVariant: 'text'
        }).then((confirm) => {
            this.props.vectorDBStore.deleteVectorDB(model.id, {
                models: this.cVectorDBs
            })
                .then(() => {
                    f.notifySuccess(`The Vector DB ${model.name} deleted successfully`);
                    confirm.hide();
                    f.handlePagination(this.cVectorDBs, this.cVectorDBs.params);
                    this.handleRefresh();
                }, f.handleError());
        }, () => {});
    }
    handlePageChange = (page) => {
        this.cVectorDBs.params.page = page-1;
        this.handleRefresh();
    }
	render() {
	    const {cVectorDBs, handleVectorDBCreate, handleVectorDBEdit, handleDeleteVectorDB} = this;

		return (
			<BaseContainer
				handleRefresh={this.handleRefresh}
				titleColAttr={{
					sm: 8,
					md: 8
				}}
				headerChildren={
					<AddButtonWithPermission
							colAttr={{
							xs: 12,
							sm: 4,
							md: 4
						}}
						permission={this.permission}
						label="CREATE VECTOR DB"
						onClick={handleVectorDBCreate}
						data-track-id="add-vector-db"
					/>
				}
			>
			    <VVectorDB
			        data={cVectorDBs}
			        permission={this.permission}
			        handleVectorDBEdit={handleVectorDBEdit}
			        handleDeleteVectorDB={handleDeleteVectorDB}
			    />
			    <PaginationComponent
                    promiseData={cVectorDBs}
                    callback={this.handlePageChange}
                />
			</BaseContainer>
		)
	}
}

export default CVectorDB;