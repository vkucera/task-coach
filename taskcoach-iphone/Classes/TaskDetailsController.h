//
//  TaskDetailsController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

#import "SwitchCell.h"
#import "DateCell.h"
#import "DescriptionCell.h"
#import "ButtonCell.h"

@class Task;

@interface TaskDetailsController : UITableViewController <UITextFieldDelegate, SwitchCellDelegate, UITextViewDelegate>
{
	Task *task;
	NSMutableArray *cells;

	ButtonCell *effortCell;
	UITableViewCell *categoriesCell;
	DateCell *startDateCell;
	DateCell *dueDateCell;
	DateCell *completionDateCell;
	
	DescriptionCell *descriptionCell;

	NSInteger categoryId;
	NSInteger trackedTasksCount;
}

- initWithTask:(Task *)task category:(NSInteger)category;

@end
