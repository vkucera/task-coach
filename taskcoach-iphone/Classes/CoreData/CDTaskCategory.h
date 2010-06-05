//
//  CDTaskCategory.h
//  
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>

@class CDCategory;
@class CDTask;

@interface CDTaskCategory :  NSManagedObject  
{
}

@property (nonatomic, retain) CDTask * task;
@property (nonatomic, retain) CDCategory * category;

@end



