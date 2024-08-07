/* library imports */
import React, { Component } from 'react';

/* other project imports */
import { STATUS} from 'common-ui/utils/globals';
import { FormHorizontal, FormGroupInput } from 'common-ui/components/form_fields';

class VReportForm extends Component {
	render() {
		const {name, description, status} = this.props.form.fields;

		return (
			<FormHorizontal>
				<FormGroupInput
					required={true}
					label="Report Name"
					placeholder="Report Name"
					fieldObj={name}
					maxLength={50}
					data-testid="report-name"
				/>
				<FormGroupInput
					fieldObj={description}
					label="Description"
					as="textarea"
					placeholder="Report Description"
					maxLength={4000}
					data-testid="desc"
				/>
			</FormHorizontal>
		);
	}
}

const report_form_def = {
	id: {},
	name: {
		defaultValue: "",
		validators: {
			errorMessage: "Required!",
			fn: (field, fields) => {
				if (!field.value || !field.value.trim()) {
					return false;
				}
				return true;
			}
		}
	},
	description: {},
	paramJson: {},
	tenantId: {},
	status: {
		defaultValue: STATUS.enabled.value
	}
}

export default VReportForm;
export {
	report_form_def
}