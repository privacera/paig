import React, {Component} from 'react';
import {observable} from 'mobx';

import BaseContainer from 'containers/base_container';
import CAIApplicationDetail from 'containers/applications/ai_applications/c_ai_application_detail';

class CAIApplicationCreate extends Component {
    @observable _vState = {
        loading: false,
        application: {}
    }
	constructor(props) {
		super(props);
	}
    handleRedirect = () => {
        this.props.history.push('/ai_applications');
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
                <CAIApplicationDetail _vState={_vState}/>
			</BaseContainer>
		)
	}
}

export default CAIApplicationCreate;