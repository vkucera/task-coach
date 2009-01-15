//
//  TaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class TaskList;

@interface TaskViewController : UITableViewController
{
	NSString *title;

	TaskList *overdueList;
	TaskList *dueTodayList;
	TaskList *startedList;
	TaskList *notStartedList;
}

- initWithTitle:(NSString *)title category:(NSInteger)categoryId;

@end
