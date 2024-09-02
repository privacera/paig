import React  from 'react';
import { observer } from 'mobx-react';

import Paper from '@material-ui/core/Paper';
import Box from '@material-ui/core/Box';

const PaperTabsContainer = observer(({children, headerProps, panelProps, paperProps,  ...props}) => {
    const [header, panel] = children
    return <Paper {...paperProps}>
        {header && <Box my={1} {...headerProps}>{header}</Box>}
        {panel && <Box px={2} {...panelProps}>{panel}</Box>}
    </Paper>
});

PaperTabsContainer.defaultProps = {
	children: [],
    headerProps: {},
    panelProps: {},
    paperProps: {}
}


export default PaperTabsContainer;