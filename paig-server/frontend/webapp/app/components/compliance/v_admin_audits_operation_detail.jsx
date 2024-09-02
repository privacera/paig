import React from 'react';
import { observer } from 'mobx-react';

import {isEqual} from 'lodash';

import Table from '@material-ui/core/Table';
import TableRow from '@material-ui/core/TableRow';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import Typography from '@material-ui/core/Typography';

import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import {ACTION_TYPE, OBJECT_TYPE_MAPPING, ADMIN_AUDITS_FIELDS_TO_HIDE_MAPPING} from 'utils/globals';

const shouldHideField = (field, fieldsToHide) => {
  return !field || fieldsToHide.includes(field);
}

const renderValue = (value) => {
	if (Array.isArray(value)) {
		return value.length > 0 ? value.join(', ') : '--';
	}
	if (typeof value === 'object' && value !== null) {
		return JSON.stringify(value, null, 2);
	}
	if (typeof value === 'boolean') {
		return value ? 'True' : 'False';
	}
	return value || '--';
}

const renderDetailView = (obj) => {
	const { action, objectState, objectStatePrevious, objectType, objectName } = obj;

	const currentState = action === ACTION_TYPE.DELETE.VALUE ? objectStatePrevious : objectState;
	const previousState = objectStatePrevious;

	if (!currentState && !previousState) return null;

	return (
		<div data-testid="admin-audits-detail-view">
			<hr/>
			<div className="m-b">
				<Typography variant="body1" data-testid="detail-title">
					<strong>{`${Utils.toTitleCase(OBJECT_TYPE_MAPPING[objectType]?.LABEL)} ${Utils.toTitleCase(objectName)} Details`}</strong>
				</Typography>
			</div>

			<Table>
				<TableHead>
					<TableRow>
						<TableCell width="30%">Fields</TableCell>
						{action === ACTION_TYPE.UPDATE.VALUE && <TableCell>Old Value</TableCell>}
						{(action === ACTION_TYPE.CREATE.VALUE || action === ACTION_TYPE.UPDATE.VALUE) && <TableCell>New Value</TableCell>}
						{action === ACTION_TYPE.REVIEW.VALUE && <TableCell>Viewed Value</TableCell>}
						{action === ACTION_TYPE.DELETE.VALUE && <TableCell>Deleted Value</TableCell>}
						{action === ACTION_TYPE.DOWNLOAD.VALUE && <TableCell>Downloaded Value</TableCell>}
					</TableRow>
				</TableHead>
				<TableBody>

					{currentState && Object.entries(currentState).map(([field, newValue]) => {

						// For CREATE, REVIEW, DELETE and DOWNLOAD action, display objectState
						if ([ACTION_TYPE.CREATE.VALUE, ACTION_TYPE.DELETE.VALUE, ACTION_TYPE.DOWNLOAD.VALUE, ACTION_TYPE.REVIEW.VALUE].includes(action)) {
							if (!newValue || (shouldHideField(field, ADMIN_AUDITS_FIELDS_TO_HIDE_MAPPING[action])) || (Array.isArray(newValue) && newValue.length === 0)) {
								return null;
							}
							let displayNewValue = renderValue(newValue);
							if (["status", "userEnforcement", "groupEnforcement"].includes(field)) {
								displayNewValue = newValue === 1 ? "Enabled" : "Disabled";
							}
							return (
								<TableRow key={field} style={{ backgroundColor: ACTION_TYPE[action].COLOR }}>
									<TableCell>{field}</TableCell>
									<TableCell colSpan={2}>{displayNewValue}</TableCell>
								</TableRow>
							);
						}

						// For UPDATE action without objectStatePrevious
						if ((shouldHideField(field, ADMIN_AUDITS_FIELDS_TO_HIDE_MAPPING[action]))) {
							return null;
						}
						let displayNewValue = renderValue(newValue);
						let displayOldValue = renderValue(previousState ? previousState[field] : null);
						const oldValue = previousState ? previousState[field] : null;                    
						if (["status", "userEnforcement", "groupEnforcement"].includes(field)) {
							displayOldValue = oldValue === 1 ? "Enabled" : "Disabled";
							displayNewValue = newValue === 1 ? "Enabled" : "Disabled";
						}
						if (action === ACTION_TYPE.UPDATE.VALUE && !isEqual(oldValue, newValue)) {
							return (
								<TableRow key={field} style={{ backgroundColor: ACTION_TYPE[action].COLOR }}>
									<TableCell>{field}</TableCell>
									<TableCell><span className='diff-danger'>{displayOldValue}</span></TableCell>
									<TableCell><span className='diff-primary'>{displayNewValue}</span></TableCell>
								</TableRow>
							);
						}
						return null;

					})}

					{ // For UPDATE action without objectStatePrevious
						!currentState && previousState && action === ACTION_TYPE.UPDATE.VALUE &&
						Object.entries(previousState).map(([field, oldValue]) => {
							if (shouldHideField(field, ADMIN_AUDITS_FIELDS_TO_HIDE_MAPPING.UPDATE)) {
								return null;
							}
							return (
								<TableRow key={field} style={{ backgroundColor: ACTION_TYPE[action].COLOR }}>
									<TableCell>{field}</TableCell>
									<TableCell><span className="diff-danger">{renderValue(oldValue)}</span></TableCell>
									<TableCell><span className='diff-primary'>{"--"}</span></TableCell>
								</TableRow>
							);
						})
					}

				</TableBody>
			</Table>
		</div>
	);
}

const VAdminAuditsOperationDetailView = observer(({ operationData }) => {
	return (
		<div>
			{f.models(operationData).map((detail, index) => (
				<div key={index}>{renderDetailView(detail)}</div>
			))}
		</div>
	)
});

export default VAdminAuditsOperationDetailView;