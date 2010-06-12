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
#import "SwitchCell.h"
#import "RecurrencePeriodCell.h"
#import "TaskDetailsRecurrencePeriodPicker.h"

@class CDTask;
@class DatePickerViewController;

@interface TaskDetailsDates : UITableViewController <SwitchCellDelegate, RecurrencePeriodCellDelegate, TaskDetailsRecurrencePeriodPickerDelegate>
{
	CDTask *task;

	TaskDetailsController *parentCtrl;
	NSMutableArray *cells;
	NSMutableArray *recCells;
	DateCell *startDateCell;
	DateCell *dueDateCell;
	DateCell *completionDateCell;
	DateCell *reminderDateCell;
	SwitchCell *recurrenceCell;
	RecurrencePeriodCell *recPeriodCell;
	SwitchCell *recSameWeekdayCell;

	DatePickerViewController *datePicker;
	TaskDetailsRecurrencePeriodPicker *periodPicker;
}

- initWithTask:(CDTask *)task parent:(TaskDetailsController *)parent;

@end
