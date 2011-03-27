//
//  SimpleTaskView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 27/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "CDList.h"

@interface SimpleTaskView : UITableViewController
{
    NSFetchedResultsController *resultsCtrl;
}

- (id)initWithList:(CDList *)list;

@end
