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

@interface TaskTableView : UITableViewController <NSFetchedResultsControllerDelegate>
{
    NSFetchedResultsController *resultsCtrl;
    CDTask *detailsTask;

    NSIndexPath *scrollTo;
    BOOL editSubject;

    IBOutlet TaskView *taskView;
}

- (void)reload;
- (void)refresh;
- (void)addTask;

@end
