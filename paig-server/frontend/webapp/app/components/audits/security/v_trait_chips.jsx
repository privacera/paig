import React, {Fragment} from 'react';

import Chip from '@material-ui/core/Chip';
import BlockIcon from '@material-ui/icons/Block';
import green from '@material-ui/core/colors/green';
import CheckCircleOutlineOutlinedIcon from '@material-ui/icons/CheckCircleOutlineOutlined';
import RemoveCircleOutlineOutlinedIcon from '@material-ui/icons/RemoveCircleOutlineOutlined';

function TraitChipList({ model }) {
    if (model.traits?.length > 0) {
        return (
            <Fragment>
                {model.traits.map((tag) => {
                    const isMaskedTrait = model.maskedTraits?.hasOwnProperty(tag);
                    let icon;
                    if (model.isAllowed || (model.isMasked && !isMaskedTrait)) {
                        icon = <CheckCircleOutlineOutlinedIcon style={{ color: green[500] }} />;
                    } else if (model.isMasked && isMaskedTrait) {
                        icon = <RemoveCircleOutlineOutlinedIcon style={{ color: "#9e9e9e" }} />;
                    } else {
                        icon = <BlockIcon style={{ color: '#ff7043' }} />;
                    }
                    return (
                        <Chip
                            key={tag}
                            label={tag}
                            size="small"
                            className="m-r-xs m-b-xs"
                            style={{
                                backgroundColor: (model.isMasked && isMaskedTrait) ? '' : (model.isMasked || model.isAllowed) ? '#DFF0D8' : '#FCE6E2',
                                color: '#333', 
                            }}
                            icon={icon}
                        />
                    );
                })}
            </Fragment>
        )
    }
    return '--';
}

export default TraitChipList;
