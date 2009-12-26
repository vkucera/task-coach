//
//  TaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

#import "PositionStore.h"

@class Task;
@class TaskList;
@class TaskCell;
@class CategoryViewController;

@interface TaskViewController : UIViewController <UIAlertViewDelegate, RestorableController>
{
	NSString *title;
	NSInteger categoryId;
	Task *parentTask;

	NSMutableArray *headers;
	BOOL isBecomingEditable;
	NSIndexPath *tapping;
	BOOL isCreatingTask;
	
	TaskCell *currentCell;
	
	UITableViewController *tableViewController;
	CategoryViewController *categoryController;
}

@property (nonatomic, readonly) UITableView *tableView;
@property (nonatomic, retain) IBOutlet UITableViewController *tableViewController;

- (IBAction)onAddTask:(UIBarButtonItem *)button;
- (IBAction)onSync:(UIBarButtonItem *)button;

- initWithTitle:(NSString *)title category:(NSInteger)categoryId categoryController:(CategoryViewController *)controller parentTask:(Task *)parent;

@end
