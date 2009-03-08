//
//  TaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class TaskList;
@class TaskCell;

@interface TaskViewController : UITableViewController <UIAlertViewDelegate>
{
	NSString *title;
	NSInteger categoryId;

	NSMutableArray *headers;
	BOOL isBecomingEditable;
	NSIndexPath *tapping;
	BOOL isCreatingTask;
	
	TaskCell *currentCell;
}

- initWithTitle:(NSString *)title category:(NSInteger)categoryId;

@end
