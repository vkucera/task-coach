//
//  TaskDetailsController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "SwitchCell.h"

@class Task;

@interface TaskDetailsController : UITableViewController <UITextFieldDelegate, SwitchCellDelegate>
{
	Task *task;
	NSMutableArray *cells;
	
	SwitchCell *startDateCell;
	UITableViewCell *startDateValueCell;
	
	SwitchCell *dueDateCell;
	UITableViewCell *dueDateValueCell;
}

- initWithTask:(Task *)task;

@end
