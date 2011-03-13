//
//  TasklistListView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class TasklistView;

@interface TasklistListView : UITableViewController <NSFetchedResultsControllerDelegate>
{
    NSFetchedResultsController *resultsCtrl;
    IBOutlet TasklistView *parent;
}

@property (nonatomic, assign) TasklistView *parent;

@end
