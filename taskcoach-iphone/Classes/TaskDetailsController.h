//
//  TaskDetailsController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "SwitchCell.h"
#import "DateCell.h"
#import "DescriptionCell.h"

@class Task;

@interface TaskDetailsController : UITableViewController <UITextFieldDelegate, SwitchCellDelegate, UITextViewDelegate>
{
	Task *task;
	NSMutableArray *cells;
	
	DateCell *startDateCell;
	DateCell *dueDateCell;
	
	DescriptionCell *descriptionCell;

	NSInteger categoryId;
}

- initWithTask:(Task *)task category:(NSInteger)category;

@end
