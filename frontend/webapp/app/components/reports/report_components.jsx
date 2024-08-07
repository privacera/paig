import React from 'react';
import { observer } from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import Box from '@material-ui/core/Box';
import Paper from '@material-ui/core/Paper';

const PaperCard = (props) => {
	const { children, boxProps = {} } = props;
	return (
		<Paper>
			<Box {...boxProps}>{children}</Box>
		</Paper>
	);
};

const TitleItem = ({ label, toolTipTitle }) => {
	return (
		<Tooltip arrow placement="top-start" title={toolTipTitle} >
			<Typography className='graph-title inline-block' gutterBottom>
				{label}
			</Typography>
		</Tooltip>
	);
}

const MetricItemBox = observer(({ _vState, toolTipLabel, toolTipTitle, fieldName }) => {
	return (
		<Grid item md={4} sm={6}>
			<PaperCard boxProps={{ p: 2 }}>
				<Tooltip arrow placement="top-start" title={toolTipTitle}>
					<Typography variant="h6" className="graph-title inline-block">{toolTipLabel}</Typography>
				</Tooltip>
				<Typography variant="h5">{_vState[fieldName]}</Typography>
			</PaperCard>
		</Grid>
	);
});

export {
	PaperCard,
	TitleItem,
	MetricItemBox
}