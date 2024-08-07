import React, {Component} from 'react';
import {observable} from 'mobx';

import BaseContainer from 'containers/base_container';
import CVectorDBDetail from 'containers/applications/vector_db/c_vector_db_detail';

class CVectorDBCreate extends Component {
    @observable _vState = {
        loading: false,
        model: {}
    }
	constructor(props) {
		super(props);
	}
    handleRedirect = () => {
        this.props.history.push('/vector_db');
    }
    handleBackButton = () => {
        this.handleRedirect();
    }
	render() {
        const {_vState, handleBackButton} = this;
		return (
			<BaseContainer
                showRefresh={false}
                showBackButton={true}
                backButtonProps={{
                    size: 'small',
                    onClick: handleBackButton
                }}
				titleColAttr={{
					sm: 8,
					md: 8
				}}
			>
                <CVectorDBDetail _vState={_vState}/>
			</BaseContainer>
		)
	}
}

export default CVectorDBCreate;