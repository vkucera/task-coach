//
//  TaskDetailsEfforts.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "ButtonCell.h"

@class Task;

@interface TaskDetailsEfforts : UITableViewController
{
	Task *task;
	ButtonCell *effortCell;
	NSInteger trackedTasksCount;
	NSInteger effortCount;
	NSInteger displayedEffortCount;
	NSInteger effortTotal;
}

- initWithTask:(Task *)task;

@end
