//
//  TaskDetailsCell.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 09/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "ImageButton.h"
#import "SmartButton.h"

@class CDTask;

@interface TaskDetailsCell : UITableViewCell <UITextFieldDelegate, UITableViewDataSource, UITableViewDelegate>
{
    IBOutlet UITextField *subject;
    IBOutlet ImageButton *completionButton;
    IBOutlet SmartButton *trackButton;

    void (^callback)(id);

    CDTask *theTask;
    
    IBOutlet UITableView *datesTable;
    IBOutlet UIDatePicker *datePicker;
}

- (void)setTask:(CDTask *)task callback:(void (^)(id))callback;
- (void)editSubject;
- (IBAction)onChangeDate:(id)sender;

@end
