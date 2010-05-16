//
//  TaskDetailsDates.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "TaskDetailsController.h"
#import "DateCell.h"

@class Task;
@class DatePickerViewController;

@interface TaskDetailsDates : UITableViewController <SwitchCellDelegate>
{
	Task *task;
	TaskDetailsController *parentCtrl;

	NSMutableArray *cells;
	DateCell *startDateCell;
	DateCell *dueDateCell;
	DateCell *completionDateCell;
	DatePickerViewController *datePicker;
}

- initWithTask:(Task *)task parent:(TaskDetailsController *)parent;

@end
