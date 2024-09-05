import React, {Fragment} from 'react';

import logoSvg from 'common-ui/images/new_images/astronaut.svg'

const ErrorLogo = ({errorCode='404'}) => {
	return (
		<Fragment>
			<div className="error-onimage">
				{errorCode}
			</div>
			<img src={logoSvg} />
		</Fragment>
	)
}

export {
	ErrorLogo
}