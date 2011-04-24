//
//  TaskTableView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CDTask;
@class TaskView;
@class TaskDetailsCell;

@interface TaskTableView : UITableViewController <NSFetchedResultsControllerDelegate>
{
    NSFetchedResultsController *resultsCtrl;
    CDTask *detailsTask;
    TaskDetailsCell *detailsCell;

    NSIndexPath *scrollTo;
    BOOL editSubject;

    IBOutlet TaskView *taskView;
    IBOutlet UIBarButtonItem *groupingButton;
    IBOutlet UIBarButtonItem *addButton;
}

@property (nonatomic, readonly) CDTask *detailsTask;

- (void)reload;
- (void)refresh;
- (void)addTask;
- (void)doneEditing;

@end
