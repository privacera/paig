import React, { useEffect } from 'react';
import { observer } from 'mobx-react';

import { FormHorizontal, FormGroupInput } from 'common-ui/components/form_fields';

const VRunReportForm = observer(({form, mode}) => {
  const { name, report_name } = form.fields;

  useEffect(() => {
    const generateReportName = () => {
      if (name.value) {
        const now = new Date();
        const formattedDate = now.toLocaleDateString('en-GB').split('/').reverse().join(''); // Format: DDMMYYYY
        const formattedTime = now.toLocaleTimeString('en-GB', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        }).replace(':', ''); // Format: HHmm
        const reportType = mode === "rerun_report" ? "rerun_report" : "report";
        return `${name.value}_${reportType}_${formattedDate}${formattedTime}`;
      }
      return '';
    };

    report_name.value = generateReportName();
  }, [name.value, report_name]);

  return (
    <FormHorizontal>
      <FormGroupInput
        textOnly={true}
        label={"Security Evaluation Name"}
        fieldObj={name}
        inputProps={{ 'data-testid': 'name-input' }}
      />
      <FormGroupInput
        required={true}
        label={"Report Name"}
        fieldObj={report_name}
        inputProps={{ 'data-testid': 'report-input' }}
      />
    </FormHorizontal>
  );
});

export default VRunReportForm;