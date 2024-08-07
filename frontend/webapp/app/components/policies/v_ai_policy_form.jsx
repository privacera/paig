import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';
import { compact } from 'lodash';

import TableContainer from '@material-ui/core/TableContainer';
import Table from '@material-ui/core/Table';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableBody from '@material-ui/core/TableBody';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import Grid from '@material-ui/core/Grid';
import CloseIcon from '@material-ui/icons/Close';
import PersonIcon from '@material-ui/icons/Person';
import PeopleIcon from '@material-ui/icons/People';
import ContactsIcon from '@material-ui/icons/Contacts';

import { PROMPT_REPLY_ACTION_TYPE } from 'utils/globals';
import { userGroupRolesLookups, sensitiveDataLookUps } from 'components/policies/field_lookups';
import {TagChip} from 'common-ui/lib/fs_select/fs_select';
import {Utils} from 'common-ui/utils/utils';
import {FormHorizontal, FormGroupInput, FormGroupSelect2, ValidationAsterisk} from 'common-ui/components/form_fields';
import { STATUS } from 'common-ui/utils/globals';

const VAIPoliciesForm = observer(({ aiPolicyFormUtil }) => {
  const form = aiPolicyFormUtil.getForm();
  const {description} = form.fields;
  return (
    <FormHorizontal alignItems="flex-start">
      <TableContainer>
        <Table className="permission-table-globals">
          <TableHead>
            <TableRow>
              <TableCell className="restriction-desc" width="300px">Description <ValidationAsterisk /></TableCell>
              <TableCell className="grip-adjustment-header restriction-users" width="300px">Users and Groups <ValidationAsterisk /></TableCell>
              <TableCell className="restriction-tags" width="350px">Content Having Tags <ValidationAsterisk /></TableCell>
              <TableCell width="0px" className="restriction-hide" ></TableCell>
              <TableCell className="text-center" className="restriction-header">Restriction</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow className="permission-row">
                <TableCell>
                  <FormGroupInput
                    fieldObj={description}
                    placeholder="Enter description"
                    variant="standard"
                    data-testid="description"
                    className="permission-dropdown-fonts"
                  />
                </TableCell>
                <PermissionRow
                  itemIndex={0}
                  descriptionField={name}
                  form={form}
                  aiPolicyFormUtil={aiPolicyFormUtil}
                  className='position-relative'
                />
              </TableRow>
            </TableBody>
        </Table>
      </TableContainer>
    </FormHorizontal>
  );
})

@observer
class PermissionRow extends Component {
  render() {
    const { aiPolicyFormUtil, itemIndex, form } = this.props;
    const data = form.toJSON();
    const { PERMISSIONS, ROLE_USER_GROUP, SENSITIVE_DATA, REQUEST_TYPE } = aiPolicyFormUtil.getPermissionErrorTypes();
    const splitDelimiter = "##__##";
    const userGroupRolesValue = aiPolicyFormUtil.getPrefillUsersGroupsRolesValues(data, splitDelimiter);

    const errorPath = `${PERMISSIONS}`;
    const errorListMap = aiPolicyFormUtil.getErrorHashMap();
    const hasRoleUserGroupError = errorListMap.get(`${errorPath}${ROLE_USER_GROUP}`) === ROLE_USER_GROUP;

    const restrictionMap = aiPolicyFormUtil.getRestrictionMap();
    const actionRequest = form.fields.prompt.value;

    const draggableProps = {
      styleProps: {}
    }
    if (!restrictionMap.has(errorPath)) {
      draggableProps.styleProps.backgroundColor = (actionRequest === PROMPT_REPLY_ACTION_TYPE.DENY.VALUE) ? "#ffefef" : "#f4fdf4";
    }

    const sensitiveData = aiPolicyFormUtil.getPrefillSensitiveData(data);
    const hasSensitiveDataError = errorListMap.get(`${errorPath}${SENSITIVE_DATA}`) === SENSITIVE_DATA;
    const hasRequestError = errorListMap.get(`${errorPath}${REQUEST_TYPE}`) === REQUEST_TYPE;

    return (
      <Fragment>
        <TableCell data-row-index={(itemIndex + 1)} style={{position: "relative"}} className="permission-inputs grip-adjustment-cell">
          <FormGroupSelect2
            error={hasRoleUserGroupError}
            required={true}
            showLabel={false}
            value={userGroupRolesValue}
            variant="standard"
            allowCreate={false}
            multiple={true}
            labelKey="label"
            valueKey="value"
            placeholder="Select Users and/or Groups"
            noOptionsText="Type to search Users and/or Groups"
            triggerOnLoad={true}
            forcePopupIcon={false}
            loadOptions={(searchString, callback) => {
              this.infoOption = null;
              userGroupRolesLookups(searchString, (options, op) => {
                this.infoOption = op;
                callback(options);
              }, `${errorPath}`);
            }}
            onChange={value => aiPolicyFormUtil.setUsersGroupsRolesChange(value, itemIndex)}
            disableCloseOnSelect={true}
            renderTags={(tagValue, getTagProps) => (
              tagValue.map((option, index) => {
                const value = ''+option.value;
                const [type, val] = compact(value.split(splitDelimiter));
                const label = <div>{getIcon(type)} {val}</div>;
                return (
                  <TagChip
                    className="permission-labels"
                    label={label}
                    {...getTagProps({ index })}
                    deleteIcon={<CloseIcon />}
                  />
                )
              })
            )}
            renderList={({options, listProps, listboxProps, getOptionProps, classes}) => {
              let len = options.length;
              return (
                <Fragment>
                  <ul className={classes.listbox} {...listProps} {...listboxProps}>
                    {
                      options.map((option, index) => {
                        const optionProps = getOptionProps({option, index});
                        let disableClass = '';
                        if (userGroupRolesValue.length &&  userGroupRolesValue[0]?.label === "Everyone") {
                          disableClass = " inactive not-allowed ";
                        }
                        return (
                          <li
                            {...optionProps}
                            className={`${classes.option}${disableClass}`}
                            style={{alignItems: 'normal'}}
                            key={option.model?.resource || index}
                          >
                            <Grid item xs={9}>
                            <span className="opacity-40 m-r-sm font-12">{option.type && getIcon(option.type.toLowerCase())}</span>
                              <span data-testid="select-option-item">{option.label}</span>
                            </Grid>
                            <Grid item xs={3} className="opacity-40 font-12">{option.type !== "OTHERS" && Utils.toTitleCase(option.type)}</Grid>
                          </li>
                        )
                      })
                    }
                  </ul>
                  {
                    this.infoOption &&
                    <Fragment>
                      <Divider />
                      <li
                        {...listProps}
                        {...listboxProps}
                        ref={null}
                        className={classes.option}
                        classes="disabled"
                        aria-disabled="true"
                        tabIndex="-1"
                        style={{backgroundColor: '#eae9e9'}}
                      >
                        <Grid item xs={12} key="count">
                          <Typography variant="caption" className="pull-right bold font-wt-500">
                            Showing Users: {this.infoOption.USERS}, Groups: {this.infoOption.GROUPS}
                          </Typography>
                        </Grid>
                      </li>
                    </Fragment>
                  }
                </Fragment>
              )
            }}
            data-testid="user-group-restriction"        
          />
        </TableCell>
        <TableCell className="permission-inputs">
          <FormGroupSelect2
            error={hasSensitiveDataError}
            required={true}
            showLabel={false}
            value={sensitiveData}
            variant="standard"
            multiple={true}
            labelKey="label"
            valueKey="value"
            placeholder="Add Tags..."
            triggerOnLoad={true}
            forcePopupIcon={false}
            loadOptions={(searchString, callback) => {
              sensitiveDataLookUps(searchString, options => callback(options));
            }}
            onChange={value => aiPolicyFormUtil.setSensitiveDataChange(value, itemIndex)}
            disableCloseOnSelect={true}
            data-testid="sensitive-data-restriction"
          />
        </TableCell>
        <TableCell colSpan={2} className="prompt-component-box">
          <PromptReplyComponent
            form={form}
          />
        </TableCell>
      </Fragment>
    );
  }
}

const PromptReplyComponent = ({form}) => {

  const {prompt, reply} = form.fields;

  return (
    <Table className='table-border'>
      <TableBody>
        <TableRow className="prompt-reponse-top-row">
          <TableCell className="prompt-response-col first">
            Prompt
          </TableCell>
          <TableCell className="permission-inputs">
            <FormGroupSelect2
              data={Object.values(PROMPT_REPLY_ACTION_TYPE)}
              labelKey="LABEL"
              valueKey="VALUE"
              openText="Options"
              disableClearable={true}
              variant="standard"
              fieldObj={prompt}
              data-testid="prompt-restriction"
            />
          </TableCell>
        </TableRow>
        <TableRow className="prompt-reponse-bottom-row">
          <TableCell className="prompt-response-col second">
            Reply
          </TableCell>
          <TableCell className="permission-inputs">
            <FormGroupSelect2
              data={Object.values(PROMPT_REPLY_ACTION_TYPE)}
              labelKey="LABEL"
              valueKey="VALUE"
              openText="Options"
              disableClearable={true}
              variant="standard"
              fieldObj={reply}
              data-testid="reply-restriction"
            />
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  )
}

const getIcon = type => {
  const common = { fontSize: "small" }
  switch(type) {
    case 'users':
      return <PersonIcon {...common} />;
    case "groups":
      return <PeopleIcon {...common} />
    case "roles":
      return <ContactsIcon {...common} />
    case "others":
      return <PeopleIcon {...common} />
  }
}


const ai_policy_form_def = {
  id: {},
  description: {
      defaultValue: "",
      validators: {
          errorMessage: 'Required!',
          fn: (field) => {
            return Utils.characterValidation(field);
          }
      }
  },
  status: {
    defaultValue: STATUS.enabled.value
  },
  users: {
    defaultValue: []
  },
  groups: {
    defaultValue: []
  },
  roles: {
    defaultValue: []
  },
  tags: {
    defaultValue: []
  },
  prompt: {
    defaultValue: PROMPT_REPLY_ACTION_TYPE.ALLOW.VALUE
  },
  reply: {
    defaultValue: PROMPT_REPLY_ACTION_TYPE.ALLOW.VALUE
  },
  enrichedPrompt: {
    defaultValue: PROMPT_REPLY_ACTION_TYPE.ALLOW.VALUE
  }
}

export default VAIPoliciesForm;
export {
  ai_policy_form_def
}