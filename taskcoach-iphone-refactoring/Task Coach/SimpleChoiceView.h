//
//  SimpleChoiceView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 17/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface SimpleChoiceView : UITableViewController
{
    NSFetchedResultsController *resultsCtrl;
    void (^completionCb)(NSManagedObject *);
}

- (id)initWithEntityName:(NSString *)name completion:(void (^)(NSManagedObject *))completion exclude:(NSManagedObject *)excl;

@end
