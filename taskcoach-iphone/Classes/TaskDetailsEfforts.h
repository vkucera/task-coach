//
//  TaskDetailsEfforts.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "ButtonCell.h"

@class CDTask;

@interface TaskDetailsEfforts : UITableViewController <NSFetchedResultsControllerDelegate>
{
	CDTask *task;
	ButtonCell *effortCell;
	NSFetchedResultsController *results;
}

- initWithTask:(CDTask *)task;

@end
