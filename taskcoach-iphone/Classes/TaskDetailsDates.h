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

@class CDTask;
@class DatePickerViewController;

@interface TaskDetailsDates : UITableViewController <SwitchCellDelegate>
{
	CDTask *task;
	NSManagedObjectID *taskID;

	TaskDetailsController *parentCtrl;

	NSMutableArray *cells;
	DateCell *startDateCell;
	DateCell *dueDateCell;
	DateCell *completionDateCell;
	DateCell *reminderDateCell;

	DatePickerViewController *datePicker;
}

- initWithTask:(CDTask *)task parent:(TaskDetailsController *)parent;

@end
