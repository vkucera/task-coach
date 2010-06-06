//
//  TaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>
#import <TapkuLibrary/ODCalendarDayTimelineView.h>

#import "PositionStore.h"

@class CategoryViewController;
@class SearchCell;
@class TaskCell;

@interface TaskViewController : UIViewController <UIAlertViewDelegate, RestorableController, UISearchBarDelegate, ODCalendarDayTimelineViewDelegate, NSFetchedResultsControllerDelegate>
{
	BOOL shouldEdit;
	BOOL isCreatingTask;

	UITableViewController *tableViewController;
	CategoryViewController *categoryController;

	SearchCell *searchCell;
	TaskCell *currentCell;
	NSIndexPath *tapping;
	NSTimer *minuteTimer;

	ODCalendarDayTimelineView *calendarView;
	UISearchBar *calendarSearch;
	UIToolbar *toolbar;

	NSFetchedResultsController *results;
	NSIndexPath *selected;
}

@property (nonatomic, readonly) UITableView *tableView;
@property (nonatomic, retain) IBOutlet UITableViewController *tableViewController;
@property (nonatomic, retain) IBOutlet ODCalendarDayTimelineView *calendarView;
@property (nonatomic, retain) IBOutlet UISearchBar *calendarSearch;
@property (nonatomic, retain) IBOutlet UIToolbar *toolbar;

- (IBAction)onAddTask:(UIBarButtonItem *)button;
- (IBAction)onSync:(UIBarButtonItem *)button;
- (IBAction)onSwitch:(UIBarButtonItem *)button;

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit;

- (void)populate;
- (NSPredicate *)predicate;

@end
