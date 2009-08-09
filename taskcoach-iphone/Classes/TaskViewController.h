//
//  TaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

#import "PositionStore.h"

@class TaskList;
@class TaskCell;

@interface TaskViewController : UIViewController <UIAlertViewDelegate, RestorableController>
{
	NSString *title;
	NSInteger categoryId;

	NSMutableArray *headers;
	BOOL isBecomingEditable;
	NSIndexPath *tapping;
	BOOL isCreatingTask;
	
	TaskCell *currentCell;
	
	UITableViewController *tableViewController;
}

@property (nonatomic, readonly) UITableView *tableView;
@property (nonatomic, retain) IBOutlet UITableViewController *tableViewController;

- (IBAction)onAddTask:(UIBarButtonItem *)button;

- initWithTitle:(NSString *)title category:(NSInteger)categoryId;

@end
