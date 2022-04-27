import React from 'react';
import CustomTab from "../../../../shared/components/Tab";

function generateExceptionTab() {
    return (
        <CustomTab label = 'Exception'>
            <div>
                <h1>Exception Tab</h1>
                <p>This is the Return Value tab</p>
            </div>
        </CustomTab>
    )
}

/*
function ExceptionTab() {
    return (
        <CustomTab tabName={'Exception'}>
            <div>
                <h1>Exception Tab</h1>
                <p>This is the Exception tab</p>
            </div>
        </CustomTab>
    );
}
*/

export default generateExceptionTab;